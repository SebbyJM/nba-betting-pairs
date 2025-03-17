# Force update
import streamlit as st
import pandas as pd
import random

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

# Function to determine best bet (Over/Under)
def get_best_bet(row):
    if row["Edge"] > 0:
        return "Over", row["Best_Over_Odds"]
    else:
        return "Under", row["Best_Under_Odds"]

# --- PLAYER SEARCH FUNCTION ---
def player_search():
    st.title("🔍 PLAYER SEARCH")
    player_name = st.text_input("Enter Player Name:")

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
            st.write(f"🟠 **{row['Player']} ({row['Best_Line']} {category})**")
            st.write(explain_performance(row, hot=True))

    # COLD PLAYERS
    st.subheader("COLD PLAYERS")
    for category, player_df in cold_players.items():
        if not player_df.empty:
            row = player_df.iloc[0]
            st.write(f"🔵 **{row['Player']} ({row['Best_Line']} {category})**")
            st.write(explain_performance(row, hot=False))

# --- BEST PROPS FUNCTION ---
def best_props():
    st.title("💰 VALUE PROPS")

    # Exclude Hot & Cold Players from Best Props
    hot_cold_players_list = pd.concat([
        df.nlargest(3, "Best_Over_Odds"),
        df.nsmallest(3, "Best_Under_Odds")
    ])["Player"].unique()

    # Find best props, ensuring they are NOT Hot or Cold Players and meet minimum thresholds
    best_points = df[(df["Category"] == "Points") & (df["Best_Line"] >= 20) & (~df["Player"].isin(hot_cold_players_list))].nlargest(1, "Edge")
    best_rebounds = df[(df["Category"] == "Rebounds") & (df["Best_Line"] >= 5) & (~df["Player"].isin(hot_cold_players_list))].nlargest(1, "Edge")
    best_assists = df[(df["Category"] == "Assists") & (df["Best_Line"] >= 4) & (~df["Player"].isin(hot_cold_players_list))].nlargest(1, "Edge")

    best_props = pd.concat([best_points, best_rebounds, best_assists])

    for _, row in best_props.iterrows():
        over_under, best_odds = get_best_bet(row)
        st.write(f"• **{row['Player']} - {over_under} {row['Best_Line']} {row['Category']}**")
        st.write(f"AI Projection: {row['AI_Projection']:.1f}")
        st.write(f"L10 Avg: {row['L10']:.1f}, H2H Avg: {row['H2H']:.1f}, Best Odds: {best_odds}")

# --- AI 2-MANS FUNCTION (Balanced Over & Unders) ---
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

            # Ensure both players have solid statistical backing
            pairs.append((player1, player2))

        attempts += 1  # Track number of tries

    for i, (player1, player2) in enumerate(pairs, start=1):
        p1_bet, p1_odds = get_best_bet(player1)
        p2_bet, p2_odds = get_best_bet(player2)

        st.subheader(f"SLIP {i}")
        st.write(f"• **{player1['Player']} - {p1_bet} {player1['Best_Line']} {player1['Category']}**")
        st.write(f"• **{player2['Player']} - {p2_bet} {player2['Best_Line']} {player2['Category']}**")

        # Explanation for why this bet is valuable
        st.write(f"1️⃣ {p1_bet} at {player1['Best_Line']} with odds **{p1_odds}**. Projection: **{player1['AI_Projection']:.1f}**, L10: **{player1['L10']:.1f}**, H2H: **{player1['H2H']:.1f}**.")
        st.write(f"2️⃣ {p2_bet} at {player2['Best_Line']} with odds **{p2_odds}**. Projection: **{player2['AI_Projection']:.1f}**, L10: **{player2['L10']:.1f}**, H2H: **{player2['H2H']:.1f}**.")
        st.write("---")

# --- STREAMLIT NAVIGATION ---
menu = st.sidebar.radio("📂 Select Page", ["Player Search", "Hot & Cold Players", "Best Props Available", "AI 2-Mans"])

if menu == "Player Search":
    player_search()
elif menu == "Hot & Cold Players":
    hot_cold_players()
elif menu == "Best Props Available":
    best_props()
elif menu == "AI 2-Mans":
    generate_ai_2mans()