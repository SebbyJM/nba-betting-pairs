import pandas as pd
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playergamelogs, scoreboardv2
from datetime import datetime
import time

HEADERS = {
    "Host": "stats.nba.com",
    "Connection": "keep-alive",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
    "Referer": "https://www.nba.com/",
}

def get_player_id(player_name):
    player_list = players.get_players()
    for player in player_list:
        if player['full_name'].lower() == player_name.lower():
            return player['id']
    return None

def get_today_matchups():
    today = datetime.today().strftime('%m/%d/%Y')
    scoreboard = scoreboardv2.ScoreboardV2(game_date=today, headers=HEADERS)
    games = scoreboard.get_normalized_dict()["GameHeader"]

    matchups = {}
    for game in games:
        matchups[game["HOME_TEAM_ID"]] = game["VISITOR_TEAM_ID"]
        matchups[game["VISITOR_TEAM_ID"]] = game["HOME_TEAM_ID"]
    return matchups

def get_team_abbreviation(team_id):
    team_list = teams.get_teams()
    for team in team_list:
        if team['id'] == team_id:
            return team['abbreviation']
    return None

def fetch_last10_avg(player_id):
    logs = playergamelogs.PlayerGameLogs(
        player_id_nullable=player_id,
        season_nullable="2024-25",
        season_type_nullable="Regular Season",
        headers=HEADERS
    ).get_data_frames()[0].head(10)

    if logs.empty:
        return None

    return {
        "L10_PTS": round(logs["PTS"].mean(), 1),
        "L10_AST": round(logs["AST"].mean(), 1),
        "L10_REB": round(logs["REB"].mean(), 1),
        "Team_ID": logs.iloc[0]["TEAM_ID"]
    }

def fetch_h2h_avg(player_id, opponent_team_abbr):
    logs = playergamelogs.PlayerGameLogs(
        player_id_nullable=player_id,
        season_nullable="2023-24",
        season_type_nullable="Regular Season",
        headers=HEADERS
    ).get_data_frames()[0]

    h2h_logs = logs[logs["MATCHUP"].str.contains(opponent_team_abbr)]

    if h2h_logs.empty:
        return {"H2H_PTS": None, "H2H_AST": None, "H2H_REB": None}

    return {
        "H2H_PTS": round(h2h_logs["PTS"].mean(), 1),
        "H2H_AST": round(h2h_logs["AST"].mean(), 1),
        "H2H_REB": round(h2h_logs["REB"].mean(), 1),
    }

def process_players(file_path):
    with open(file_path, 'r') as file:
        player_names = [line.strip() for line in file]

    today_matchups = get_today_matchups()

    # Prepare separate data lists for each category
    points_data, rebounds_data, assists_data = [], [], []

    for name in player_names:
        print(f"🚀 Processing {name}...")
        player_id = get_player_id(name)

        if player_id is None:
            print(f"❌ No ID found for {name}, skipping.")
            continue

        l10_stats = fetch_last10_avg(player_id)
        if l10_stats is None:
            print(f"⚠️ No L10 data for {name}, skipping.")
            continue

        team_id = l10_stats["Team_ID"]

        if team_id not in today_matchups:
            print(f"⚠️ {name} has no game today.")
            continue

        opponent_team_id = today_matchups[team_id]
        opponent_abbr = get_team_abbreviation(opponent_team_id)

        h2h_stats = fetch_h2h_avg(player_id, opponent_abbr)

        # Append Points data
        points_data.append({
            "Player": name,
            "L10_PTS": l10_stats["L10_PTS"],
            "H2H_PTS": h2h_stats["H2H_PTS"],
        })

        # Append Rebounds data
        rebounds_data.append({
            "Player": name,
            "L10_REB": l10_stats["L10_REB"],
            "H2H_REB": h2h_stats["H2H_REB"],
        })

        # Append Assists data
        assists_data.append({
            "Player": name,
            "L10_AST": l10_stats["L10_AST"],
            "H2H_AST": h2h_stats["H2H_AST"],
        })

        time.sleep(1.5)

    # Save each CSV clearly separated by category
    pd.DataFrame(points_data).to_csv("Player_Points_L10_H2H.csv", index=False)
    pd.DataFrame(rebounds_data).to_csv("Player_Rebounds_L10_H2H.csv", index=False)
    pd.DataFrame(assists_data).to_csv("Player_Assists_L10_H2H.csv", index=False)

    print("✅ All data successfully saved!")

if __name__ == "__main__":
    process_players("players.txt")