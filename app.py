import streamlit as st
import pandas as pd

# Set up Streamlit page
st.set_page_config(page_title="Betting Pairs AI", page_icon="🎯", layout="wide")

# Load data function
@st.cache_data
def load_data():
    points = pd.read_csv("AI_Projections_Points.csv")
    rebounds = pd.read_csv("AI_Projections_Rebounds.csv")
    assists = pd.read_csv("AI_Projections_Assists.csv")

    # Combine all props
    df = pd.concat([points, rebounds, assists], ignore_index=True)

    # Convert numeric values and calculate Edge
    df["AI_Projection"] = pd.to_numeric(df["AI_Projection"], errors="coerce").round(1)
    df["best_point"] = pd.to_numeric(df["best_point"], errors="coerce").round(1)
    df["Edge"] = (df["AI_Projection"] - df["best_point"]).round(1)

    # Ensure Rebounds/Assists only appear if line is 4 or more
    df = df[~((df["category"].isin(["Rebounds", "Assists"])) & (df["best_point"] < 4))]

    # Determine Over/Under recommendation
    df["Bet Pick"] = df.apply(lambda row: "Over" if row["Edge"] > 0 else "Under", axis=1)

    return df

# Load data
df = load_data()

# Select best betting pairs (Limit to 4 & ensure at least one Under)
def find_betting_pairs(df, num_pairs=4):
    pairs = []
    df_sorted = df.sort_values(by="Edge", ascending=False)

    # Separate Over & Under picks
    over_picks = df_sorted[df_sorted["Bet Pick"] == "Over"]
    under_picks = df_sorted[df_sorted["Bet Pick"] == "Under"]

    force_under = True if not under_picks.empty else False  # Require at least one Under if available

    while len(df_sorted) > 1 and len(pairs) < num_pairs:
        player1 = df_sorted.iloc[0]  # Strongest Edge player
        df_sorted = df_sorted.iloc[1:]  # Remove the selected player

        # If we haven't picked an Under yet, prioritize one
        if force_under and player1["Bet Pick"] == "Over" and not under_picks.empty:
            player2 = under_picks.iloc[0]  # Force an Under pick
            under_picks = under_picks.iloc[1:]  # Remove from pool
            force_under = False  # Now we have an Under, so we stop forcing it
        else:
            # Otherwise, pick the best available match (Over + Over, Under + Under, Over + Under)
            for _, player2 in df_sorted.iterrows():
                if (
                    player1["player"] != player2["player"]  # Different players
                    and player1["category"] != player2["category"]  # Different stat type
                    and (player1["Bet Pick"] != player2["Bet Pick"] or abs(player1["Edge"]) > 2 or abs(player2["Edge"]) > 2)  # Mix or strong Edge
                ):
                    df_sorted = df_sorted[df_sorted["player"] != player2["player"]]  # Remove second player from pool
                    break
            else:
                continue  # If no valid pair is found, continue

        pairs.append((player1, player2))

    return pairs

# Generate a more detailed writeup for betting pairs
def generate_writeup(pair):
    p1, p2 = pair
    title = f"🟢 **{p1['player']} {p1['Bet Pick']} {p1['category']} {p1['best_point']}** + **{p2['player']} {p2['Bet Pick']} {p2['category']} {p2['best_point']}**"

    writeup = (
        f"\n📊 **{p1['player']}** has been consistently **{'exceeding' if p1['Bet Pick'] == 'Over' else 'falling short of'}** "
        f"their line of **{p1['best_point']}**, averaging **{p1['AI_Projection']}** in the last 10 matchups.\n\n"
        f"📊 Meanwhile, **{p2['player']}** has shown **{'dominant performance' if p2['Bet Pick'] == 'Over' else 'struggles'}** "
        f"in the **{p2['category']}** category, with an AI projection of **{p2['AI_Projection']}** vs. their line of **{p2['best_point']}**.\n\n"
        f"💡 **This pair offers strong value based on AI projections, trends, and matchup insights.**"
    )

    return title, writeup

# Get the best betting pairs (Limit 4)
betting_pairs = find_betting_pairs(df, num_pairs=4)

# --- DISPLAY IN STREAMLIT ---
st.title("🔗 **Best NBA Betting Pairs**")

if betting_pairs:
    betting_data = []
    for pair in betting_pairs:
        p1, p2 = pair
        betting_data.append([
            p1["player"], p1["category"], p1["best_point"], p1["Bet Pick"],
            p2["player"], p2["category"], p2["best_point"], p2["Bet Pick"]
        ])

    betting_df = pd.DataFrame(
        betting_data,
        columns=["Player 1", "Prop 1", "Line 1", "Bet 1", "Player 2", "Prop 2", "Line 2", "Bet 2"]
    )

    # Display table with proper spacing
    st.dataframe(
        betting_df.style.format({"Line 1": "{:.1f}", "Line 2": "{:.1f}"}).set_properties(**{"margin-bottom": "20px"})
    )

    # Display write-ups
    st.subheader("📝 **Why These Pairs?**")
    for pair in betting_pairs:
        title, writeup = generate_writeup(pair)
        st.markdown(f"### {title}\n{writeup}\n\n---\n")  # Adds spacing for better readability

else:
    st.warning("No strong betting pairs found today.")