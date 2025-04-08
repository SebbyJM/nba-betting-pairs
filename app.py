
import streamlit as st
import pandas as pd
import random
from scipy.stats import norm

# 🎨 Fonts: Orbitron (titles), Roboto (content)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Roboto:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Roboto', sans-serif;
}

h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
}

h1 {
    font-size: 32px;
    text-align: center;
    font-weight: 700;
    margin-bottom: 5px;
}

@media (max-width: 768px) {
    h1 {
        font-size: 24px !important;
    }
    .ai-subtitle {
        font-size: 12px !important;
    }
}

.card-hover:hover {
    box-shadow: 0 0 20px #89CFF0;
    transform: scale(1.01);
    transition: 0.2s ease-in-out;
}

body, .stApp {
    background-color: black;
    color: white;
}
.css-1d391kg, .css-18e3th9 {
    background-color: #111;
}
.stTextInput, .stButton>button {
    border-radius: 4px;
    border: 3px solid black;
    background-color: black;
    color: gray;
}
.stButton>button:hover {
    background-color: #89CFF0;
    color: black;
}
hr {
    border: none;
    height: 2px;
    background: linear-gradient(to right, #89CFF0, transparent);
    margin: 25px 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1>
    <span style="color: white;">CHEAT THE BOOKS</span> 
    <span style="color: #89CFF0;">AI</span>
</h1>
<div class="ai-subtitle" style="text-align:center; margin-top:-10px; font-family:monospace; font-size:13px; color:gray;">
    ⌛ Generating high-value props using machine learning...
</div>
""", unsafe_allow_html=True)

df_points = pd.read_csv("Final_Projections_POINTS.csv")
df_rebounds = pd.read_csv("Final_Projections_REBOUNDS.csv")
df_assists = pd.read_csv("Final_Projections_ASSISTS.csv")
df_cs2 = pd.read_csv("SOLAR CS2 AI - Sheet1.csv")
df_defense = pd.read_csv("defensive_ratings.csv")

df_points["Category"] = "Points"
df_rebounds["Category"] = "Rebounds"
df_assists["Category"] = "Assists"
df = pd.concat([df_points, df_rebounds, df_assists], ignore_index=True)

df = df.merge(df_defense[['TEAM', 'DEF RTG', 'DEF RTG RANK']],
              left_on='Opponent', right_on='TEAM', how='left')

def get_best_bet(row):
    if row["Edge"] > 0 and row["Best_Over_Odds"] <= -110:
        return "Over", row["Best_Over_Odds"]
    elif row["Edge"] < 0 and row["Best_Under_Odds"] <= -110:
        return "Under", row["Best_Under_Odds"]
    else:
        return "Fade", None

def calculate_confidence(row, best_odds):
    edge_score = min(max(abs(row["Edge"]), 0), 1)
    l10_diff = row["L10"] - row["Best_Line"]
    l10_score = min(max(l10_diff / row["Best_Line"], 0), 1)
    odds_score = 1 if best_odds >= -115 else 0.5 if best_odds >= -130 else 0.3

    defense_penalty = 0
    if not pd.isna(row.get("DEF RTG RANK")) and row["DEF RTG RANK"] <= 10:
        defense_penalty = 0.2

    confidence = (edge_score * 0.4 + l10_score * 0.4 + odds_score * 0.2)
    confidence = confidence * (1 - defense_penalty)
    return int(min(max(confidence * 100, 10), 100))

def calculate_probability(row):
    projection = row['AI_Projection']
    line = row['Best_Line']
    std_dev = row.get('STDDEV', 4.0)
    z = (projection - line) / std_dev
    prob_over = 1 - norm.cdf(z)
    prob_under = norm.cdf(z)
    return round(prob_over * 100), round(prob_under * 100)

def matchup_note(row):
    team = row.get("TEAM", "Unknown")
    rank = row.get("DEF RTG RANK", None)
    if pd.isna(rank) or pd.isna(team):
        return "Matchup data unavailable"
    rank = int(rank)
    if rank >= 20:
        return f"Great matchup ({team} #{rank})"
    elif rank <= 10:
        return f"Tough matchup ({team} #{rank})"
    else:
        return f"Neutral matchup ({team} #{rank})"

def convert_odds(odds):
    if odds is None:
        return 0
    if odds < 0:
        return -100 / odds
    else:
        return odds / 100

def adjusted_projection(row):
    proj = row["AI_Projection"]

    # Apply defensive adjustment
    rank = row.get("DEF RTG RANK", None)
    if not pd.isna(rank):
        if rank <= 5:
            proj *= 0.9  # Tough defense
        elif rank >= 25:
            proj *= 1.1  # Easy defense

    # Use L5 if available to adjust projection
    if "L5" in row and not pd.isna(row["L5"]):
        proj = row["L5"] * 0.6 + row["L10"] * 0.4

    return proj

def is_valid_value_pick(row):
    over_under, best_odds = get_best_bet(row)
    if over_under == "Fade" or best_odds is None:
        return False

    # Calculate AI probability
    prob_over, prob_under = calculate_probability(row)
    prob = prob_over if over_under == "Over" else prob_under
    if prob < 35:  # lower threshold slightly
        return False

    # Optional: only warn, don't block, cold streak
    # if is_on_cold_streak(row): return False

    return True

def is_on_cold_streak(row):
    last3 = row.get("Last3")
    if isinstance(last3, list):
        hits = [val >= row["Best_Line"] for val in last3]
        return sum(hits) <= 1  # 0 or 1 hits in last 3 = cold streak
    return False

# --- Other functions omitted for brevity ---
# Will send final completed script in parts if too large

def player_search():
    st.title("NBA SEARCH")

    all_players = sorted(df["Player"].unique())
    typed = st.text_input("Start typing a player name (e.g. 'john'):").strip()

    if typed:
        matching = [p for p in all_players if typed.lower() in p.lower()]
        if matching:
            selected = st.selectbox("Matching players:", matching)
            player_data = df[df["Player"] == selected]

            st.markdown("----")
            st.markdown(f"### {selected}")

            for cat in ["Points", "Rebounds", "Assists"]:
                stat = player_data[player_data["Category"] == cat]
                if not stat.empty:
                    row = stat.iloc[0]
                    bet, odds = get_best_bet(row)

                    st.markdown(f"#### {cat}")
                    st.markdown(f"📊 Projection: {row['AI_Projection']:.1f} | 🔟 L10: {row['L10']:.1f} | 💰 Odds: {odds}  \n")

                    if bet != "Fade" and odds is not None:
                        prob_over, prob_under = calculate_probability(row)
                        prob = prob_over if bet == "Over" else prob_under
                        tough = row["DEF RTG RANK"] <= 5 if not pd.isna(row["DEF RTG RANK"]) else False

                        st.markdown(f"**Best Bet:** {bet} {row['Best_Line']}")
                        st.markdown(f"🤖 AI Probability: {prob}%")
                        st.markdown(f"🛡️ {matchup_note(row)}{' 🔥 Tough Matchup!' if tough else ''}")
                        st.progress(prob / 100)
                    else:
                        st.markdown("⚠️ No strong value detected for this prop.\n")



def best_props():
    st.title("NBA VALUE")

    excluded_top_odds = pd.concat([
        df.nlargest(3, "Best_Over_Odds"),
        df.nsmallest(3, "Best_Under_Odds")
    ])["Player"].unique()

    df_filtered = df.copy()
    df_filtered["Odds_Score"] = df_filtered.apply(
        lambda row: convert_odds(get_best_bet(row)[1]), axis=1
    )
    df_filtered["Value_Score"] = df_filtered["Edge"] + (df_filtered["Odds_Score"] / 75)

    def is_valid_value_pick(row):
        over_under, best_odds = get_best_bet(row)
        if over_under == "Fade" or best_odds is None:
            return False
        prob_over, prob_under = calculate_probability(row)
        prob = prob_over if over_under == "Over" else prob_under
        return prob >= 35

    df_filtered = df_filtered[df_filtered.apply(is_valid_value_pick, axis=1)]

    selected_players = []
    used_opponents = []

    def select_best(category, min_line, max_odds, min_def_rank):
        return df_filtered[
            (df_filtered["Category"] == category) &
            (df_filtered["Best_Line"] >= min_line) &
            (df_filtered["Best_Over_Odds"] <= max_odds) &
            (df_filtered["DEF RTG RANK"] > min_def_rank) &
            (~df_filtered["Player"].isin(excluded_top_odds)) &
            (~df_filtered["Player"].isin(selected_players)) &
            (~df_filtered["Opponent"].isin(used_opponents))
        ].nlargest(1, "Value_Score")

    best_points = select_best("Points", 18.5, -120, 7)
    selected_players += best_points["Player"].tolist()
    used_opponents += best_points["Opponent"].tolist()

    best_rebounds = select_best("Rebounds", 4.0, -140, 5)
    selected_players += best_rebounds["Player"].tolist()
    used_opponents += best_rebounds["Opponent"].tolist()

    best_assists = select_best("Assists", 4.0, -140, 5)

    best = pd.concat([best_points, best_rebounds, best_assists])

    if best.empty:
        st.warning("No value found.")
        return

    for _, row in best.iterrows():
        over_under, best_odds = get_best_bet(row)
        prob_over, prob_under = calculate_probability(row)
        ai_prob = prob_over if over_under == "Over" else prob_under
        tough_matchup = row["DEF RTG RANK"] <= 5
        cold_streak = is_on_cold_streak(row)
        warning = "⚠️ On a cold streak (1 or fewer hits in last 3)" if cold_streak else ""

        with st.expander(f"► {row['Player']} – {over_under} {row['Best_Line']} {row['Category']}"):
            st.markdown(f'''
                <div class='card-hover' style='background-color:#1a1a1a; padding:15px; border-radius:10px;'>
                    📊 <strong>Projection:</strong> {row['AI_Projection']:.1f}<br>
                    🔟 <strong>L10:</strong> {row['L10']:.1f}<br>
                    💰 <strong>Odds:</strong> {best_odds}<br>
                    🛡️ <strong>Matchup:</strong> {matchup_note(row)}{' 🔥 Tough Matchup!' if tough_matchup else ''}<br>
                    {warning}
                </div>
            ''', unsafe_allow_html=True)
            st.progress(ai_prob / 100)
            st.write(f"AI Probability: {ai_prob}%")
def generate_ai_2mans():
    st.title("NBA AI")

    st.sidebar.header('🤖 AI PLAYS FILTERS')
    num_players = st.sidebar.selectbox('Players per slip', [1, 2, 3, 4], index=1)
    min_odds = st.sidebar.number_input('Minimum Odds (e.g. -130)', min_value=-300, max_value=-100, value=-130)
    pick_category = st.sidebar.selectbox('Pick Category', ["All", "Points", "Rebounds", "Assists"])
    bet_type = st.sidebar.selectbox('Bet Type', ["Both", "Overs Only", "Unders Only"])
    ignore_tough = st.sidebar.checkbox("Exclude Top 10 Defense Matchups")

    df_filtered = df.copy()

    # Category-specific minimum lines
    def meets_line_threshold(row):
        if row["Category"] == "Points":
            return row["Best_Line"] >= 17.5
        else:  # Rebounds or Assists
            return row["Best_Line"] >= 4.0

    df_filtered = df_filtered[df_filtered.apply(meets_line_threshold, axis=1)]
    if pick_category != "All":
        df_filtered = df_filtered[df_filtered["Category"] == pick_category]

    df_filtered["Odds_Score"] = df_filtered.apply(lambda row: convert_odds(get_best_bet(row)[1]), axis=1)
    df_filtered["Value_Score"] = df_filtered["Edge"] + (df_filtered["Odds_Score"] / 75)

    def is_valid_two_man_pick(row):
        bet, odds = get_best_bet(row)
        if bet == "Fade" or odds is None:
            return False
        if odds > min_odds:
            return False
        if bet_type == "Overs Only" and bet != "Over":
            return False
        if bet_type == "Unders Only" and bet != "Under":
            return False
        if ignore_tough and not pd.isna(row.get("DEF RTG RANK")) and row["DEF RTG RANK"] <= 10:
            return False
        if "Last3" in row and isinstance(row["Last3"], list):
            hits = [val >= row["Best_Line"] for val in row["Last3"]]
            if sum(hits) <= 1:
                return False
        return True

    df_filtered = df_filtered[df_filtered.apply(is_valid_two_man_pick, axis=1)]
    df_filtered = df_filtered.sort_values(by="Value_Score", ascending=False)

    pairs, attempts, used_players = [], 0, set()

    while len(pairs) < 3 and len(df_filtered) >= num_players and attempts < 30:
        sample = df_filtered.sample(num_players)
        if any(player in used_players for player in sample["Player"]):
            attempts += 1
            continue
        pairs.append(sample)
        used_players.update(sample["Player"])
        df_filtered = df_filtered[~df_filtered["Player"].isin(used_players)]
        attempts += 1

    if not pairs:
        st.write("No picks match your filter criteria. Try adjusting your filters.")
        return

    for i, slip in enumerate(pairs, 1):
        st.subheader(f"SLIP {i}")
        for _, player in slip.iterrows():
            bet, odds = get_best_bet(player)
            prob_over, prob_under = calculate_probability(player)
            ai_prob = prob_over if bet == "Over" else prob_under
            with st.expander(f"► {player['Player']} – {bet} {player['Best_Line']} {player['Category']}"):
                st.markdown(f'''
                    <div class='card-hover' style='background-color:#1a1a1a; padding:15px; border-radius:10px;'>
                        📊 <strong>Projection:</strong> {player['AI_Projection']:.1f}<br>
                        🔟 <strong>L10:</strong> {player['L10']:.1f}<br>
                        💰 <strong>Odds:</strong> {odds}<br>
                        🛡️ <strong>Matchup:</strong> {matchup_note(player)}
                    </div>
                ''', unsafe_allow_html=True)
                st.progress(ai_prob / 100)
                st.write(f"AI Probability: {ai_prob}%")

def lol_value_props():
    st.title("LoL VALUE")

    lol_df = pd.read_csv("SOLAR AI LoL - PROJ.csv")

    all_rows = []

    for _, row in lol_df.iterrows():
        # Kills
        if pd.notna(row["KILLS"]) and pd.notna(row["K PROJ."]):
            diff = row["K PROJ."] - row["KILLS"]
            all_rows.append({
                "Player": row["PLAYER"],
                "Team": row["TEAM"],
                "Line": row["KILLS"],
                "Proj": row["K PROJ."],
                "Type": "Kills",
                "Diff": diff,
                "TeamOdds": row["TEAM ODDS"],
                "Bet": "Over" if diff > 0 else "Under"
            })
        # Assists
        if pd.notna(row["ASSISTS"]) and pd.notna(row["A PROJ."]):
            diff = row["A PROJ."] - row["ASSISTS"]
            all_rows.append({
                "Player": row["PLAYER"],
                "Team": row["TEAM"],
                "Line": row["ASSISTS"],
                "Proj": row["A PROJ."],
                "Type": "Assists",
                "Diff": diff,
                "TeamOdds": row["TEAM ODDS"],
                "Bet": "Over" if diff > 0 else "Under"
            })

    df_lol = pd.DataFrame(all_rows)

    # Best Over & Under value
    over = df_lol[df_lol["Diff"] > 0].nlargest(1, "Diff")
    under = df_lol[df_lol["Diff"] < 0].nsmallest(1, "Diff")
    value_df = pd.concat([over, under])

    for _, row in value_df.iterrows():
        with st.expander(f"► {row['Player']}"):
            st.markdown(f'''
                <div class='card-hover' style='background-color:#1a1a1a; padding:15px; border-radius:10px;'>
                    📊 <strong>Stat Type:</strong> {row['Type']}<br>
                    🔢 <strong>Line:</strong> {row['Line']}<br>
                    🤖 <strong>Projection:</strong> {row['Proj']:.2f}<br>
                    📈 <strong>Difference:</strong> {row['Diff']:.2f}<br>
                    🏅 <strong>Team:</strong> {row['Team']} ({row['TeamOdds']})<br>
                    📉 <strong>Bet:</strong> {row['Bet']}
                </div>
            ''', unsafe_allow_html=True)

def lol_2mans():
    st.title("LoL AI")

    df_lol = pd.read_csv("SOLAR AI LoL - PROJ.csv")

    all_rows = []
    for _, row in df_lol.iterrows():
        # Kills
        if pd.notna(row["KILLS"]) and pd.notna(row["K PROJ."]):
            diff = row["K PROJ."] - row["KILLS"]
            all_rows.append({
                "Player": row["PLAYER"],
                "Team": row["TEAM"],
                "Line": row["KILLS"],
                "Proj": row["K PROJ."],
                "Type": "Kills",
                "Diff": diff,
                "TeamOdds": row["TEAM ODDS"],
                "Bet": "Over" if diff > 0 else "Under"
            })
        # Assists
        if pd.notna(row["ASSISTS"]) and pd.notna(row["A PROJ."]):
            diff = row["A PROJ."] - row["ASSISTS"]
            all_rows.append({
                "Player": row["PLAYER"],
                "Team": row["TEAM"],
                "Line": row["ASSISTS"],
                "Proj": row["A PROJ."],
                "Type": "Assists",
                "Diff": diff,
                "TeamOdds": row["TEAM ODDS"],
                "Bet": "Over" if diff > 0 else "Under"
            })

    df_combined = pd.DataFrame(all_rows)

    # Sort by absolute difference and mix top 5 Over and top 5 Under
    top_over = df_combined[df_combined["Diff"] > 0].nlargest(5, "Diff")
    top_under = df_combined[df_combined["Diff"] < 0].nsmallest(5, "Diff")
    top_picks = pd.concat([top_over, top_under]).sample(frac=1).reset_index(drop=True)

    if top_picks.empty:
        st.warning("No 2-man candidates found.")
        return

    # Group in slips of 2
    num_slips = min(3, len(top_picks) // 2)
    for i in range(num_slips):
        st.subheader(f"SLIP {i+1}")
        slip = top_picks.iloc[i*2:i*2+2]
        for _, row in slip.iterrows():
            with st.expander(f"► {row['Player']} – {row['Type']}"):
                st.markdown(f'''
                    <div class='card-hover' style='background-color:#1a1a1a; padding:15px; border-radius:10px;'>
                        📊 <strong>Line:</strong> {row['Line']}<br>
                        🤖 <strong>Projection:</strong> {row['Proj']:.2f}<br>
                        📈 <strong>Difference:</strong> {row['Diff']:.2f}<br>
                        🏅 <strong>Team:</strong> {row['Team']} ({row['TeamOdds']})<br>
                        📉 <strong>Bet:</strong> {row['Bet']}
                    </div>
                ''', unsafe_allow_html=True)


# Sidebar navigation with single section active at a time
section = st.sidebar.radio("Select Section", ["🏀 NBA", "🎮 League of Legends"])

if section == "🏀 NBA":
    nba_page = st.sidebar.radio("NBA Pages", ["Search", "Value", "AI"], key="nba_menu")

    if nba_page == "Search":
        player_search()
    elif nba_page == "Value":
        best_props()
    elif nba_page == "AI":
        generate_ai_2mans()

elif section == "🎮 League of Legends":
    lol_page = st.sidebar.radio("LoL Pages", ["Value", "AI"], key="lol_menu")

    if lol_page == "Value":
        lol_value_props()
    elif lol_page == "AI":
        lol_2mans()


# --- Footer ---
st.markdown("""
    <hr>
    <p style="text-align: center; font-size: 12px; color: gray;">
        Sharing this site and data will result in immediate loss of access with no refund.<br>
        Questions?:<br>
        X: @SolarJenda | Discord: SolarJenda
    </p>
""", unsafe_allow_html=True)
