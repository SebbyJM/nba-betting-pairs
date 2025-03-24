# Force update
import streamlit as st
import pandas as pd
import random

# Google Fonts - Roboto
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Roboto', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# Hide Streamlit default UI + custom hover
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .card-hover:hover {
        box-shadow: 0 0 15px #89CFF0;
        transform: scale(1.01);
        transition: 0.2s ease-in-out;
    }
    </style>
""", unsafe_allow_html=True)

# Custom styling
st.markdown("""
    <style>
        body, .stApp {
            background-color: black;
            color: white;
        }
        .title-text {
            text-align: center;
            font-weight: bold;
            font-size: 36px;
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
        .footer {
            text-align: center;
            font-size: 12px;
            color: gray;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style="text-align: center; font-weight: bold;">
        <span style="color: white;">CHEAT THE BOOKS</span> 
        <span style="color: #89CFF0;">AI</span>
    </h1>
""", unsafe_allow_html=True)

# Load data
df_points = pd.read_csv("Final_Projections_POINTS.csv")
df_rebounds = pd.read_csv("Final_Projections_REBOUNDS.csv")
df_assists = pd.read_csv("Final_Projections_ASSISTS.csv")
df_cs2 = pd.read_csv("SOLAR CS2 AI - Sheet1.csv")
df_defense = pd.read_csv("defensive_ratings.csv")

df_points["Category"] = "Points"
df_rebounds["Category"] = "Rebounds"
df_assists["Category"] = "Assists"
df = pd.concat([df_points, df_rebounds, df_assists], ignore_index=True)

# Merge defensive rankings clearly
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

    # Defensive penalty (Top 10 = reduce confidence)
    defense_penalty = 0
    if not pd.isna(row.get("DEF RTG RANK")) and row["DEF RTG RANK"] <= 10:
        defense_penalty = 0.2  # up to -20%

    confidence = (edge_score * 0.4 + l10_score * 0.4 + odds_score * 0.2)
    confidence = confidence * (1 - defense_penalty)  # apply penalty
    return int(min(max(confidence * 100, 10), 100))

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

# NBA SEARCH (updated clearly)
def player_search():
    st.title("🏀 NBA SEARCH")
    player_name = st.text_input(" Enter Player Name:")
    if player_name:
        player_data = df[df["Player"].str.lower() == player_name.lower()]
        if player_data.empty:
            st.write("❌ No player found.")
        else:
            for _, row in player_data.iterrows():
                over_under, best_odds = get_best_bet(row)
                st.write(f"**{row['Player']}** - {over_under} {row['Best_Line']} {row['Category']}")
                st.write(f"AI Projection: {row['AI_Projection']:.1f}")
                st.write(f"L10 Avg: {row['L10']:.1f}, H2H Avg: {row['H2H']:.1f}, Best Odds: {best_odds}")
                st.write(f"🛡️ Matchup: {matchup_note(row)}")

# HOT & COLD (unchanged clearly)
def hot_cold_players():
    st.title("📊 HOT & COLD PLAYERS")
    def get_performance_change(row): return round(row["L10"] - row["Best_Line"], 1)
    def explain(row, hot): return (
        f"Exceeding line by **{get_performance_change(row)}**" if hot else f"Falling short by **{abs(get_performance_change(row))}**"
    )
    hot = {...} # keep your original hot/cold code unchanged here
def hot_cold_players():
    st.title("📊 HOT & COLD PLAYERS")
    def get_performance_change(row): return round(row["L10"] - row["Best_Line"], 1)
    def explain(row, hot): return (
        f"Exceeding line by **{get_performance_change(row)}**" if hot else f"Falling short by **{abs(get_performance_change(row))}**"
    )

    hot = {
        "Points": df[(df["Category"] == "Points") & (df["Best_Line"] >= 18.5) & (df["L10"] > df["Best_Line"])].nlargest(1, "Best_Over_Odds"),
        "Rebounds": df[(df["Category"] == "Rebounds") & (df["Best_Line"] >= 4.0) & (df["L10"] > df["Best_Line"])].nlargest(1, "Best_Over_Odds"),
        "Assists": df[(df["Category"] == "Assists") & (df["Best_Line"] >= 4.0) & (df["L10"] > df["Best_Line"])].nlargest(1, "Best_Over_Odds")
    }
    cold = {
        "Points": df[(df["Category"] == "Points") & (df["Best_Line"] >= 18.5) & (df["L10"] < df["Best_Line"])].nlargest(1, "Best_Under_Odds"),
        "Rebounds": df[(df["Category"] == "Rebounds") & (df["Best_Line"] >= 4.0) & (df["L10"] < df["Best_Line"])].nlargest(1, "Best_Under_Odds"),
        "Assists": df[(df["Category"] == "Assists") & (df["Best_Line"] >= 4.0) & (df["L10"] < df["Best_Line"])].nlargest(1, "Best_Under_Odds")
    }

    with st.expander("🔥 HOT PLAYERS"):
        for cat, df_ in hot.items():
            if not df_.empty:
                row = df_.iloc[0]
                st.write(f"**{row['Player']}** ({row['Best_Line']} {cat})")
                st.write(explain(row, True))

    with st.expander("⛄️ COLD PLAYERS"):
        for cat, df_ in cold.items():
            if not df_.empty:
                row = df_.iloc[0]
                st.write(f"**{row['Player']}** ({row['Best_Line']} {cat})")
                st.write(explain(row, False))

def best_props():
    st.title("💰 VALUE PROPS")

    excluded = pd.concat([
        df.nlargest(3, "Best_Over_Odds"),
        df.nsmallest(3, "Best_Under_Odds")
    ])["Player"].unique()

    # Exclude top 5 defensive matchups (lowest ranks = toughest)
    df_filtered = df[~df["DEF RTG RANK"].le(5, fill_value=False)]

    best_points = df_filtered[(df_filtered["Category"] == "Points") & (df_filtered["Best_Line"] >= 20.5) & (~df_filtered["Player"].isin(excluded))].nlargest(1, "Edge")
    best_rebounds = df_filtered[(df_filtered["Category"] == "Rebounds") & (df_filtered["Best_Line"] >= 4.0) & (~df_filtered["Player"].isin(excluded))].nlargest(1, "Edge")
    best_assists = df_filtered[(df_filtered["Category"] == "Assists") & (df_filtered["Best_Line"] >= 4.0) & (~df_filtered["Player"].isin(excluded))].nlargest(1, "Edge")
    best = pd.concat([best_points, best_rebounds, best_assists])

    for _, row in best.iterrows():
        over_under, best_odds = get_best_bet(row)
        if over_under != "Fade":
            confidence = calculate_confidence(row, best_odds)
            with st.expander(f"► {row['Player']} – {over_under} {row['Best_Line']} {row['Category']}"):
                st.markdown(f"""
                <div class='card-hover' style='background-color:#1a1a1a; padding:15px; border-radius:10px;'>
                    📊 <strong>Projection:</strong> {row['AI_Projection']:.1f}<br>
                    🔟 <strong>L10:</strong> {row['L10']:.1f}<br>
                    🤺 <strong>H2H:</strong> {row['H2H']:.1f}<br>
                    💰 <strong>Odds:</strong> {best_odds}<br>
                    🛡️ <strong>Matchup:</strong> {matchup_note(row)}
                </div>""", unsafe_allow_html=True)
                st.progress(confidence)
                st.write(f"Confidence: {confidence}%")

# AI 2-MANS (updated with defensive matchups)

def generate_ai_2mans():
    st.title("🤖 AI PLAYS")

    st.sidebar.header('🤖 AI PLAYS FILTERS')
    num_players = st.sidebar.selectbox('Players per slip', [1, 2, 3, 4], index=1)
    min_odds = st.sidebar.number_input('Minimum Odds (e.g. -130)', min_value=-300, max_value=-100, value=-130)
    pick_category = st.sidebar.selectbox('Pick Category', ["All", "Points", "Rebounds", "Assists"])
    bet_type = st.sidebar.selectbox('Bet Type', ["Both", "Overs Only", "Unders Only"])
    ignore_tough = st.sidebar.checkbox("Exclude Top 10 Defense Matchups")

    if pick_category == "Points":
        filtered = df[(df["Category"] == "Points") & (df["Best_Line"] >= 17.5)]
    elif pick_category == "Rebounds":
        filtered = df[(df["Category"] == "Rebounds") & (df["Best_Line"] >= 4.0)]
    elif pick_category == "Assists":
        filtered = df[(df["Category"] == "Assists") & (df["Best_Line"] >= 4.0)]
    else:
        filtered = df[((df["Category"] == "Points") & (df["Best_Line"] >= 17.5)) |
                      ((df["Category"].isin(["Rebounds", "Assists"])) & (df["Best_Line"] >= 4.0))]

    def valid_pick(row):
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
        return True

    filtered = filtered[filtered.apply(valid_pick, axis=1)]
    pairs, attempts, used_players = [], 0, set()

    while len(pairs) < 3 and len(filtered) >= num_players and attempts < 30:
        sample = filtered.sample(num_players)
        if any(player in used_players for player in sample["Player"]):
            attempts += 1
            continue
        pairs.append(sample)
        used_players.update(sample["Player"])
        filtered = filtered[~filtered["Player"].isin(used_players)]
        attempts += 1

    if not pairs:
        st.write("No picks match your filter criteria. Try adjusting your filters.")
        return

    for i, slip in enumerate(pairs, 1):
        st.subheader(f"SLIP {i}")
        for _, player in slip.iterrows():
            bet, odds = get_best_bet(player)
            confidence = calculate_confidence(player, odds)
            with st.expander(f"► {player['Player']} – {bet} {player['Best_Line']} {player['Category']}"):
                st.markdown(f"""
                <div class='card-hover' style='background-color:#1a1a1a; padding:15px; border-radius:10px;'>
                    📊 <strong>Projection:</strong> {player['AI_Projection']:.1f}<br>
                    🔟 <strong>L10:</strong> {player['L10']:.1f}<br>
                    🤺 <strong>H2H:</strong> {player['H2H']:.1f}<br>
                    💰 <strong>Odds:</strong> {odds}<br>
                    🛡️ <strong>Matchup:</strong> {matchup_note(player)}
                </div>""", unsafe_allow_html=True)
                st.progress(confidence)
                st.write(f"Confidence: {confidence}%")


# CS2 SEARCH (unchanged)
def cs2_player_search():
    st.title("🎮 CS2 SEARCH")
    name = st.text_input("Enter Player Name:")
    if name:
        data = df_cs2[df_cs2["Player"].str.contains(name, case=False, na=False)]
        if data.empty:
            st.write("❌ No CS2 player found.")
        else:
            kills = data[data["Player"].str.endswith("(K)")]
            hs = data[~data["Player"].str.endswith("(K)")]
            st.write(f"**{name}**")
            if not kills.empty:
                st.write(f"🔫 Kills: Avg {kills.iloc[0]['Average']:.1f}, Line {kills.iloc[0]['Line']}")
            if not hs.empty:
                st.write(f"👤 Headshots: Avg {hs.iloc[0]['Average']:.1f}, Line {hs.iloc[0]['Line']}")

# --- NAVIGATION ---
menu = st.sidebar.radio("📂 Select Page", ["NBA Search", "Hot & Cold", "Value Props", "AI Plays", "CS2 Search"])
if menu == "NBA Search":
    player_search()
elif menu == "Hot & Cold":
    hot_cold_players()
elif menu == "Value Props":
    best_props()
elif menu == "AI Plays":
    generate_ai_2mans()
elif menu == "CS2 Search":
    cs2_player_search()

# --- Footer ---
st.markdown("""
    <hr>
    <p style="text-align: center; font-size: 12px; color: gray;">
        Sharing this site and data will result in immediate loss of access with no refund.<br>
        Questions?:<br>
        X: @SolarJenda | Discord: SolarJenda
    </p>
""", unsafe_allow_html=True)
