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

# Load the necessary CSVs
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

# --- CS2 Player Search ---
def cs2_player_search():
    st.title("CS2 Player Search")

    # List of all CS2 players
    all_players = sorted(df_cs2["Player"].unique())

    # User can type to search for a player
    typed = st.text_input("Start typing a CS2 player name (e.g. 'hades'):").strip()

    if typed:
        # Filter matching players
        matching = [p for p in all_players if typed.lower() in p.lower()]
        if matching:
            selected = st.selectbox("Matching players:", matching)
            player_data = df_cs2[df_cs2["Player"] == selected]

            # Display the selected player's stats
            st.markdown(f"### {selected}")
            st.markdown(f"**Kill Line**: {player_data['Kill_Line'].values[0]}")
            st.markdown(f"**Kill Projection**: {player_data['Kill_Projection'].values[0]}")
            st.markdown(f"**HS Line**: {player_data['HS_Line'].values[0]}")
            st.markdown(f"**HS Projection**: {player_data['HS_Projection'].values[0]}")

# --- CS2 Projections Table with Color Coding ---
def cs2_projections():
    st.title("CS2 Projections")

    # Function to apply color gradients based on projections vs line
    def apply_gradient(val, line):
        if val > line:
            color = f"background-color: rgba(0, 255, 0, {(val - line) / line});"  # Green for higher projections
        else:
            color = f"background-color: rgba(255, 0, 0, {(line - val) / line});"  # Red for lower projections
        return color

    # Ensure that columns are treated as floats for correct comparison
    df_cs2["Kill_Line"] = df_cs2["Kill_Line"].astype(float)
    df_cs2["Kill_Projection"] = df_cs2["Kill_Projection"].astype(float)
    df_cs2["HS_Line"] = df_cs2["HS_Line"].astype(float)
    df_cs2["HS_Projection"] = df_cs2["HS_Projection"].astype(float)

    # Create new columns for color gradients
    df_cs2["Kill_Color"] = df_cs2.apply(lambda row: apply_gradient(row["Kill_Projection"], row["Kill_Line"]), axis=1)
    df_cs2["HS_Color"] = df_cs2.apply(lambda row: apply_gradient(row["HS_Projection"], row["HS_Line"]), axis=1)

    # Display the table with color gradients
    st.dataframe(df_cs2.style.applymap(lambda x: 'background-color: green', subset=['Kill_Color', 'HS_Color'])
                    .applymap(lambda x: 'background-color: red', subset=['Kill_Color', 'HS_Color']))

# --- CS2 Value Props ---
def cs2_value_props():
    st.title("CS2 Value Props")

    # Calculate confidence based on projection vs line
    def calculate_confidence(row):
        proj_kills = row["Kill_Projection"]
        proj_hs = row["HS_Projection"]
        line_kills = row["Kill_Line"]
        line_hs = row["HS_Line"]

        # Example confidence metric (you can adjust it)
        confidence_kills = abs(proj_kills - line_kills) / line_kills
        confidence_hs = abs(proj_hs - line_hs) / line_hs

        return round(max(confidence_kills, confidence_hs) * 100, 1)

    df_cs2["Confidence"] = df_cs2.apply(calculate_confidence, axis=1)

    # Display the top 3 value props based on confidence
    best_value_props = df_cs2.nlargest(3, "Confidence")
    for _, row in best_value_props.iterrows():
        st.subheader(f"Best Value Prop: {row['Player']} - {row['Team']}")
        st.markdown(f"**Kill Line**: {row['Kill_Line']} | **Kill Projection**: {row['Kill_Projection']}")
        st.markdown(f"**HS Line**: {row['HS_Line']} | **HS Projection**: {row['HS_Projection']}")
        st.progress(row["Confidence"] / 100)  # Show confidence meter

# --- Sidebar Navigation ---
def navigation():
    section = st.sidebar.radio("Select Section", ["🏀 NBA", "⚔️ CS2", "🎮 League of Legends"])

    if section == "🏀 NBA":
        # Existing NBA functionality
        nba_page = st.sidebar.radio("NBA Pages", ["Search", "Value", "AI"], key="nba_menu")
        if nba_page == "Search":
            player_search()
        elif nba_page == "Value":
            best_props()
        elif nba_page == "AI":
            generate_ai_2mans()

    elif section == "⚔️ CS2":
        cs2_page = st.sidebar.radio("CS2 Pages", ["Search Player", "Projections", "Value Props"], key="cs2_menu")
        if cs2_page == "Search Player":
            cs2_player_search()
        elif cs2_page == "Projections":
            cs2_projections()
        elif cs2_page == "Value Props":
            cs2_value_props()

    elif section == "🎮 League of Legends":
        st.title("League of Legends")
        st.markdown("<h2 style='color:yellow;'>⚠️ UNDER MAINTENANCE ⚠️</h2>", unsafe_allow_html=True)

# Run the app
navigation()

# --- Footer ---
st.markdown("""
    <hr>
    <p style="text-align: center; font-size: 12px; color: gray;">
        Sharing this site and data will result in immediate loss of access with no refund.<br>
        Questions?:<br>
        X: @SolarJenda | Discord: SolarJenda
    </p>
""", unsafe_allow_html=True)
