# Force update
import streamlit as st
import pandas as pd
import random

# --- CUSTOM PAGE STYLE ---
st.markdown(
    """
    <style>
        /* Background color */
        body, .stApp {
            background-color: black;
            color: white;
        }

        /* Title Styling */
        .title-text {
            text-align: center;
            font-weight: bold;
            font-size: 36px;
        }
        
        /* Sidebar */
        .css-1d391kg, .css-18e3th9 {
            background-color: #111; /* Dark Sidebar */
        }

        /* Buttons & Text Inputs */
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
        
        /* Footer */
        .footer {
            text-align: center;
            font-size: 12px;
            color: gray;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Custom Title (Added at the top)
st.markdown(
    """
    <h1 style="text-align: center; font-weight: bold;">
        <span style="color: white;">CHEAT THE BOOKS</span> 
        <span style="color: #89CFF0;">AI</span>
    </h1>
    """,
    unsafe_allow_html=True
)

# Load the final projections
df_points = pd.read_csv("Final_Projections_POINTS.csv")
df_rebounds = pd.read_csv("Final_Projections_REBOUNDS.csv")
df_assists = pd.read_csv("Final_Projections_ASSISTS.csv")

# Ensure category labels are consistent
df_points["Category"] = "Points"
df_rebounds["Category"] = "Rebounds"
df_assists["Category"] = "Assists"

# Combine all categories
df = pd.concat([df_points, df_rebounds, df_assists], ignore_index=True)

# Load CS2 Data
df_cs2 = pd.read_csv("SOLAR CS2 AI - Sheet1.csv")

def get_best_bet(row):
    best_over_odds = row["Best_Over_Odds"]
    best_under_odds = row["Best_Under_Odds"]

    if row["Edge"] > 0 and best_over_odds <= -110:
        return "Over", best_over_odds
    elif row["Edge"] < 0 and best_under_odds <= -110:
        return "Under", best_under_odds
    else:
        return "No Bet", None

# --- PLAYER SEARCH FUNCTION ---
def player_search():
    st.title("🏀 NBA SEARCH")
    player_name = st.text_input(" Enter Player Name:")

    if player_name:
        player_data = df[df["Player"].str.lower() == player_name.lower()]

        if player_data.empty:
            st.write("❌ No player found. Check the name and try again.")
        else:
            for _, row in player_data.iterrows():
                over_under, best_odds = get_best_bet(row)
                st.write(f"**{row['Player']} - {over_under} {row['Best_Line']} {row['Category']}**")
                st.write(f"AI Projection: {row['AI_Projection']:.1f}")
                st.write(f"L10 Avg: {row['L10']:.1f}, H2H Avg: {row['H2H']:.1f}, Best Odds: {best_odds}")

# --- HOT & COLD PLAYERS FUNCTION ---
def hot_cold_players():
    st.title("📊 HOT & COLD PLAYERS")

    # Function to calculate L10 performance change
    def get_performance_change(row):
        return round(row["L10"] - row["Best_Line"], 1)

    # Generate explanation
    def explain_performance(row, hot=True):
        change = get_performance_change(row)
        if hot:
            return f"Exceeding line by **{change}** in L10 games."
        else:
            return f"Struggling to reach the line, falling short by **{abs(change)}**."

    # Select top 1 hot & cold player per category (by L10 vs Line and Odds)
    hot_players = {
        "Points": df[(df["Category"] == "Points") & (df["L10"] > df["Best_Line"])].nlargest(1, "Best_Over_Odds"),
        "Rebounds": df[(df["Category"] == "Rebounds") & (df["L10"] > df["Best_Line"])].nlargest(1, "Best_Over_Odds"),
        "Assists": df[(df["Category"] == "Assists") & (df["L10"] > df["Best_Line"])].nlargest(1, "Best_Over_Odds")
    }

    cold_players = {
        "Points": df[(df["Category"] == "Points") & (df["L10"] < df["Best_Line"])].nlargest(1, "Best_Under_Odds"),
        "Rebounds": df[(df["Category"] == "Rebounds") & (df["L10"] < df["Best_Line"])].nlargest(1, "Best_Under_Odds"),
        "Assists": df[(df["Category"] == "Assists") & (df["L10"] < df["Best_Line"])].nlargest(1, "Best_Under_Odds")
    }

    # HOT PLAYERS
    st.subheader("HOT PLAYERS")
    for category, player_df in hot_players.items():
        if not player_df.empty:
            row = player_df.iloc[0]
            st.write(f"🔥 **{row['Player']} ({row['Best_Line']} {category})**")
            st.write(explain_performance(row, hot=True))

    # COLD PLAYERS
    st.subheader("COLD PLAYERS")
    for category, player_df in cold_players.items():
        if not player_df.empty:
            row = player_df.iloc[0]
            st.write(f"⛄️ **{row['Player']} ({row['Best_Line']} {category})**")
            st.write(explain_performance(row, hot=False))

def best_props():
    st.title("💰 VALUE PROPS")

    # Exclude Hot & Cold Players from Best Props
    hot_cold_players_list = pd.concat([
        df.nlargest(3, "Best_Over_Odds"),
        df.nsmallest(3, "Best_Under_Odds")
    ])["Player"].unique()

    # Select best props **ensuring we get one per category**
    best_points = df[(df["Category"] == "Points") & (df["Best_Line"] >= 18.5) & (~df["Player"].isin(hot_cold_players_list))].nlargest(1, "Edge")
    best_rebounds = df[(df["Category"] == "Rebounds") & (~df["Player"].isin(hot_cold_players_list))].nlargest(1, "Edge")
    best_assists = df[(df["Category"] == "Assists") & (~df["Player"].isin(hot_cold_players_list))].nlargest(1, "Edge")

    best_props = pd.concat([best_points, best_rebounds, best_assists])

    # Display results (ensuring at least one per category)
    for _, row in best_props.iterrows():
        over_under, best_odds = get_best_bet(row)
        if over_under != "No Bet":  # Ensure only strong bets are shown
            st.write(f"• **{row['Player']} - {over_under} {row['Best_Line']} {row['Category']}**")
            st.write(f"AI Projection: {row['AI_Projection']:.1f}")
            st.write(f"L10 Avg: {row['L10']:.1f}, H2H Avg: {row['H2H']:.1f}, Best Odds: {best_odds}")

def generate_ai_2mans():
    st.title("🤖 AI 2-MANS")

    # Filter for Rebounds & Assists only, ensuring Best_Line is at least 4
    df_filtered = df[(df["Category"].isin(["Rebounds", "Assists"])) & (df["Best_Line"] >= 4)]

    pairs = []
    attempts = 0  # Prevent infinite loops

    while len(pairs) < 3 and len(df_filtered) > 1 and attempts < 10:
        player1 = df_filtered.sample(1).iloc[0]
        df_filtered = df_filtered[df_filtered["Player"] != player1["Player"]]

        if len(df_filtered) > 0:
            player2 = df_filtered.sample(1).iloc[0]
            df_filtered = df_filtered[df_filtered["Player"] != player2["Player"]]

            # Ensure both players have valid bets
            p1_bet, p1_odds = get_best_bet(player1)
            p2_bet, p2_odds = get_best_bet(player2)

            if p1_bet != "No Bet" and p2_bet != "No Bet":
                pairs.append((player1, player2))

        attempts += 1  # Track number of tries

    # If fewer than 3 pairs were found, fill the rest with any available bets
    while len(pairs) < 3 and not df_filtered.empty:
        player = df_filtered.sample(1).iloc[0]
        df_filtered = df_filtered[df_filtered["Player"] != player["Player"]]

        p_bet, p_odds = get_best_bet(player)
        if p_bet != "No Bet":
            pairs.append((player, None))  # Single player added if no pair found

    for i, pair in enumerate(pairs, start=1):
        st.subheader(f"SLIP {i}")

        if pair[1] is None:
            player = pair[0]
            bet, odds = get_best_bet(player)
            st.write(f"• **{player['Player']} - {bet} {player['Best_Line']} {player['Category']}**")
            st.write(f"📊 Odds: **{odds}**, Projection: **{player['AI_Projection']:.1f}**, L10 Avg: **{player['L10']:.1f}**, 23/24 H2H: **{player['H2H']:.1f}**")
        else:
            player1, player2 = pair
            p1_bet, p1_odds = get_best_bet(player1)
            p2_bet, p2_odds = get_best_bet(player2)

            st.write(f"• **{player1['Player']} - {p1_bet} {player1['Best_Line']} {player1['Category']}**")
            st.write(f"• **{player2['Player']} - {p2_bet} {player2['Best_Line']} {player2['Category']}**")
            st.write(f"📊 Odds: **{p1_odds}**, Projection: **{player1['AI_Projection']:.1f}**, L10 Avg: **{player1['L10']:.1f}**, 23/24 H2H: **{player1['H2H']:.1f}**")
            st.write(f"📊 Odds: **{p2_odds}**, Projection: **{player2['AI_Projection']:.1f}**, L10 Avg: **{player2['L10']:.1f}**, 23/24 H2H: **{player2['H2H']:.1f}**")
        st.write("---")

# --- CS2 PLAYER SEARCH ---
def cs2_player_search():
    st.title("🎮 CS2 SEARCH")

    player_name = st.text_input("Enter Player Name:")

    if player_name:
        player_data = df_cs2[df_cs2["Player"].str.contains(player_name, case=False, na=False)]

        if player_data.empty:
            st.write("❌ No CS2 player found. Check the name and try again.")
        else:
            kills = player_data[player_data["Player"].str.endswith("(K)")]
            headshots = player_data[~player_data["Player"].str.endswith("(K)")]

            st.write(f"**{player_name}**")
            if not kills.empty:
                st.write(f"🔫 Kills: Avg {kills.iloc[0]['Average']:.1f}, Line {kills.iloc[0]['Line']}")
            if not headshots.empty:
                st.write(f"👤 Headshots: Avg {headshots.iloc[0]['Average']:.1f}, Line {headshots.iloc[0]['Line']}")

# --- STREAMLIT NAVIGATION ---
menu = st.sidebar.radio("📂 Select Page", ["NBA Search", "Hot & Cold", "Value Props", "AI 2-Mans", "CS2 Search"])

if menu == "NBA Search":
    player_search()
elif menu == "Hot & Cold":
    hot_cold_players()
elif menu == "Value Props":
    best_props()
elif menu == "AI 2-Mans":
    generate_ai_2mans()
elif menu == "CS2 Search":
    cs2_player_search()

# Footer (Added at the bottom)
st.markdown(
    """
    <hr>
    <p style="text-align: center; font-size: 12px; color: gray;">
        Sharing this site and data will result in immediate loss of access with no refund.<br>
        Questions?:<br>
        X: @SolarJenda | Discord: SolarJenda
    </p>
    """,
    unsafe_allow_html=True
)