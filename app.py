import streamlit as st
import pandas as pd
import random

# Set page title
st.set_page_config(page_title="🎯 AI Betting Pairs", page_icon="📊", layout="wide")

# Load data
@st.cache_data
def load_data():
    points_df = pd.read_csv("AI_Projections_Points.csv")
    rebounds_df = pd.read_csv("AI_Projections_Rebounds.csv")
    assists_df = pd.read_csv("AI_Projections_Assists.csv")

    # Convert columns to numeric
    for df in [points_df, rebounds_df, assists_df]:
        df["AI_Projection"] = pd.to_numeric(df["AI_Projection"], errors="coerce").round(1)
        df["best_point"] = pd.to_numeric(df["best_point"], errors="coerce").round(1)
        
        # Ensure "Edge" column exists
        if "Edge" not in df.columns:
            df["Edge"] = (df["AI_Projection"] - df["best_point"]).round(1)
    
    # Filter valid lines (min 4.0 for rebounds & assists)
    rebounds_df = rebounds_df[rebounds_df["best_point"] >= 4.0]
    assists_df = assists_df[assists_df["best_point"] >= 4.0]

    return points_df, rebounds_df, assists_df

points_df, rebounds_df, assists_df = load_data()

# Function to get best betting pairs
def get_best_pairs():
    best_points = points_df.nlargest(10, "Edge")
    best_rebounds = rebounds_df.nlargest(10, "Edge")
    best_assists = assists_df.nlargest(10, "Edge")

    best_pairs = []

    while len(best_points) > 0 and len(best_rebounds) > 0 and len(best_assists) > 0 and len(best_pairs) < 4:
        datasets = [best_points, best_rebounds, best_assists]
        random.shuffle(datasets)  # Shuffle dataset order for variety

        # Pick first player from one dataset
        player1_df = datasets.pop(random.randint(0, len(datasets) - 1)).sample(1).iloc[0]
        
        # Pick second player from another dataset
        player2_df = datasets.pop(random.randint(0, len(datasets) - 1)).sample(1).iloc[0]

        # Determine best Over/Under bet for each player
        player1_bet = "Over" if player1_df["Edge"] > 0 else "Under"
        player2_bet = "Over" if player2_df["Edge"] > 0 else "Under"

        best_pairs.append({
            "Player 1": player1_df["player"],
            "Bet": player1_bet,
            "Prop 1": player1_df["category"],
            "Line 1": player1_df["best_point"],
            "AI Proj 1": player1_df["AI_Projection"],
            "Edge 1": player1_df["Edge"],
            "Player 2": player2_df["player"],
            "Bet": player2_bet,
            "Prop 2": player2_df["category"],
            "Line 2": player2_df["best_point"],
            "AI Proj 2": player2_df["AI_Projection"],
            "Edge 2": player2_df["Edge"],
        })

        # Remove selected players from all datasets to avoid repeats
        best_points = best_points[best_points["player"] != player1_df["player"]]
        best_rebounds = best_rebounds[best_rebounds["player"] != player1_df["player"]]
        best_assists = best_assists[best_assists["player"] != player1_df["player"]]

        best_points = best_points[best_points["player"] != player2_df["player"]]
        best_rebounds = best_rebounds[best_rebounds["player"] != player2_df["player"]]
        best_assists = best_assists[best_assists["player"] != player2_df["player"]]

    return best_pairs

# Generate betting pairs
pairs = get_best_pairs()

# Display table
if pairs:
    st.dataframe(pd.DataFrame(pairs), use_container_width=True)

# Generate detailed write-ups
st.write("")
st.write("### 📊 Betting Insights")
for pair in pairs:
    p1_name, p1_bet, p1_prop, p1_line, p1_proj, p1_edge = (
        pair["Player 1"], pair["Bet"], pair["Prop 1"], pair["Line 1"], pair["AI Proj 1"], pair["Edge 1"]
    )
    p2_name, p2_bet, p2_prop, p2_line, p2_proj, p2_edge = (
        pair["Player 2"], pair["Bet"], pair["Prop 2"], pair["Line 2"], pair["AI Proj 2"], pair["Edge 2"]
    )

    st.write(f"**{p1_name} {p1_bet} {p1_line} {p1_prop} + {p2_name} {p2_bet} {p2_line} {p2_prop}**")
    
    # Write-up for Player 1
    st.write(f"📊 **{p1_name}** has been averaging **{p1_proj}** in the last 10 games, "
             f"compared to a line of **{p1_line}**. With an edge of **{p1_edge}**, the **{p1_bet}** looks favorable.")

    # Write-up for Player 2
    st.write(f"📊 **{p2_name}** has been recording **{p2_proj}** on average recently, "
             f"against a set line of **{p2_line}**. The AI projects a **{p2_bet}** as the best value play.")

    st.write("---")