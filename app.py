
# Force update
import streamlit as st
import pandas as pd
import random

# Hide Streamlit default UI
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

df_points["Category"] = "Points"
df_rebounds["Category"] = "Rebounds"
df_assists["Category"] = "Assists"
df = pd.concat([df_points, df_rebounds, df_assists], ignore_index=True)

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
    confidence = int((edge_score * 0.4 + l10_score * 0.4 + odds_score * 0.2) * 100)
    return min(max(confidence, 10), 100)

# NBA SEARCH
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

# HOT & COLD
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

# VALUE PROPS
def best_props():
    st.title("💰 VALUE PROPS")
    excluded = pd.concat([
        df.nlargest(3, "Best_Over_Odds"),
        df.nsmallest(3, "Best_Under_Odds")
    ])["Player"].unique()

    best_points = df[(df["Category"] == "Points") & (df["Best_Line"] >= 18.5) & (~df["Player"].isin(excluded))].nlargest(1, "Edge")
    best_rebounds = df[(df["Category"] == "Rebounds") & (df["Best_Line"] >= 4.0) & (~df["Player"].isin(excluded))].nlargest(1, "Edge")
    best_assists = df[(df["Category"] == "Assists") & (df["Best_Line"] >= 4.0) & (~df["Player"].isin(excluded))].nlargest(1, "Edge")
    best = pd.concat([best_points, best_rebounds, best_assists])

    for _, row in best.iterrows():
        over_under, best_odds = get_best_bet(row)
        if over_under != "No Bet":
            confidence = calculate_confidence(row, best_odds)
            with st.expander(f"► {row['Player']} – {over_under} {row['Best_Line']} {row['Category']}"):
                st.markdown(f"""
                <div class='card-hover' style='background-color:#1a1a1a; padding:15px; border-radius:10px;'>
                    <p>📊 <strong>Projection:</strong> {row['AI_Projection']:.1f}<br>
                    🔟 <strong>L10:</strong> {row['L10']:.1f}<br>
                    🤺 <strong>H2H:</strong> {row['H2H']:.1f}<br>
                    💰 <strong>Odds:</strong> {best_odds}</p>
                </div>
                """, unsafe_allow_html=True)
                st.progress(confidence)
                st.write(f"Confidence: {confidence}%")

# AI 2-MANS
def generate_ai_2mans():
    st.title("🤖 AI 2-MANS")
    filtered = df[(df["Category"].isin(["Rebounds", "Assists"])) & (df["Best_Line"] >= 4)]
    pairs, attempts = [], 0

    while len(pairs) < 3 and len(filtered) > 1 and attempts < 10:
        p1 = filtered.sample(1).iloc[0]
        filtered = filtered[filtered["Player"] != p1["Player"]]
        if get_best_bet(p1)[0].lower() == "fade": continue
        if len(filtered) > 0:
            p2 = filtered.sample(1).iloc[0]
            filtered = filtered[filtered["Player"] != p2["Player"]]
            if get_best_bet(p2)[0].lower() != "fade":
                pairs.append((p1, p2))
        attempts += 1

    while len(pairs) < 3 and not filtered.empty:
        p = filtered.sample(1).iloc[0]
        filtered = filtered[filtered["Player"] != p["Player"]]
        if get_best_bet(p)[0].lower() != "fade":
            pairs.append((p, None))

    for i, pair in enumerate(pairs, 1):
        st.subheader(f"SLIP {i}")
        if pair[1] is None:
            p = pair[0]
            b, o = get_best_bet(p)
            conf = calculate_confidence(p, o)
            with st.expander(f"🎯 {p['Player']} – {b} {p['Best_Line']} {p['Category']}"):
                st.markdown(f"""<div class='card-hover' style='background-color:#1a1a1a; padding:15px; border-radius:10px;'>
                <p>📊 <strong>Projection:</strong> {p['AI_Projection']:.1f}<br>🔟 L10: {p['L10']:.1f}<br> 🤺 H2H: {p['H2H']:.1f}<br>💰 Odds: {o}</p></div>""", unsafe_allow_html=True)
                st.progress(conf)
                st.write(f"Confidence: {conf}%")
        else:
            p1, p2 = pair
            b1, o1 = get_best_bet(p1)
            b2, o2 = get_best_bet(p2)
            conf1 = calculate_confidence(p1, o1)
            conf2 = calculate_confidence(p2, o2)
            with st.expander(f"► {p1['Player']} + {p2['Player']}"):
                st.markdown(f"""<div class='card-hover' style='background-color:#1a1a1a; padding:15px; border-radius:10px;'>
                <p><strong>{p1['Player']} – {b1} {p1['Best_Line']} {p1['Category']}</strong><br>📊 {p1['AI_Projection']:.1f}, 🔟 {p1['L10']:.1f}, 🤺 {p1['H2H']:.1f}, 💰 {o1}</p><br>
                <p><strong>{p2['Player']} – {b2} {p2['Best_Line']} {p2['Category']}</strong><br>📊 {p2['AI_Projection']:.1f}, 🔟 {p2['L10']:.1f}, 🤺 {p2['H2H']:.1f}, 💰 {o2}</p></div>""", unsafe_allow_html=True)
                st.progress(conf1)
                st.write(f"Confidence: {conf1}%")
                st.progress(conf2)
                st.write(f"Confidence: {conf2}%")

# CS2 SEARCH
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

# --- Footer ---
st.markdown("""
    <hr>
    <p style="text-align: center; font-size: 12px; color: gray;">
        Sharing this site and data will result in immediate loss of access with no refund.<br>
        Questions?:<br>
        X: @SolarJenda | Discord: SolarJenda
    </p>
""", unsafe_allow_html=True)
