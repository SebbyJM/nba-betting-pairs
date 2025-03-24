import pandas as pd

# Updated file paths for L10 + H2H data (now includes Opponent)
l10_h2h_files = {
    "POINTS": "Player_Points_L10_H2H.csv",
    "REBOUNDS": "Player_Rebounds_L10_H2H.csv",
    "ASSISTS": "Player_Assists_L10_H2H.csv"
}

# File paths for cleaned best odds
cleaned_odds_files = {
    "POINTS": "Cleaned_Best_Odds_POINTS.csv",
    "REBOUNDS": "Cleaned_Best_Odds_REBOUNDS.csv",
    "ASSISTS": "Cleaned_Best_Odds_ASSISTS.csv"
}

# Output files
output_files = {
    "POINTS": "Merged_Betting_Data_POINTS.csv",
    "REBOUNDS": "Merged_Betting_Data_REBOUNDS.csv",
    "ASSISTS": "Merged_Betting_Data_ASSISTS.csv"
}

# Merge each category separately
for category in ["POINTS", "REBOUNDS", "ASSISTS"]:
    try:
        # Load L10 + H2H Data (includes Opponent now)
        l10_h2h_df = pd.read_csv(l10_h2h_files[category])

        # Load Cleaned Odds Data
        odds_df = pd.read_csv(cleaned_odds_files[category])

        # Merge on Player name
        merged_df = pd.merge(odds_df, l10_h2h_df, on="Player", how="inner")

        # Save merged data
        merged_df.to_csv(output_files[category], index=False)
        print(f"✅ Merged data saved: {output_files[category]}")

    except Exception as e:
        print(f"❌ Error merging {category}: {e}")
