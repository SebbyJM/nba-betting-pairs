import pandas as pd

# Load datasets
ai_points = pd.read_csv("AI_Projections_POINTS.csv")
ai_rebounds = pd.read_csv("AI_Projections_REBOUNDS.csv")
ai_assists = pd.read_csv("AI_Projections_ASSISTS.csv")

odds_points = pd.read_csv("Cleaned_Best_Odds_POINTS.csv")
odds_rebounds = pd.read_csv("Cleaned_Best_Odds_REBOUNDS.csv")
odds_assists = pd.read_csv("Cleaned_Best_Odds_ASSISTS.csv")

# Now includes Opponent clearly:
l10_h2h_points = pd.read_csv("Player_Points_L10_H2H.csv")
l10_h2h_rebounds = pd.read_csv("Player_Rebounds_L10_H2H.csv")
l10_h2h_assists = pd.read_csv("Player_Assists_L10_H2H.csv")

# Function to merge AI Projections, Odds, and L10/H2H Stats
def merge_data(ai_df, odds_df, l10_h2h_df, category):
    merged_df = ai_df.merge(odds_df, on="Player", how="left") \
                     .merge(l10_h2h_df, on="Player", how="left")

    # Rename best odds column
    merged_df.rename(columns={"Best_Point": "Best_Line"}, inplace=True)

    # ✅ Ensure L10 and H2H values are merged
    if category == "POINTS":
        merged_df.rename(columns={"L10_PTS": "L10", "H2H_PTS": "H2H"}, inplace=True)
    elif category == "REBOUNDS":
        merged_df.rename(columns={"L10_REB": "L10", "H2H_REB": "H2H"}, inplace=True)
    elif category == "ASSISTS":
        merged_df.rename(columns={"L10_AST": "L10", "H2H_AST": "H2H"}, inplace=True)

    # Ensure Edge is calculated properly
    merged_df["Edge"] = merged_df["AI_Projection"] - merged_df["Best_Line"]

    # Keep the Opponent column (already merged from l10_h2h)
    final_cols = ["Player", "Opponent", "Best_Line", "AI_Projection", "L10", "H2H",
                  "Best_Over_Odds", "Best_Under_Odds", "Edge"]
    
    # Reorder and keep only necessary columns
    merged_df = merged_df[final_cols]

    # Save to CSV
    merged_df.to_csv(f"Final_Projections_{category}.csv", index=False)
    print(f"✅ Saved Final_Projections_{category}.csv")

# Merge all categories
merge_data(ai_points, odds_points, l10_h2h_points, "POINTS")
merge_data(ai_rebounds, odds_rebounds, l10_h2h_rebounds, "REBOUNDS")
merge_data(ai_assists, odds_assists, l10_h2h_assists, "ASSISTS")

print("✅ Merging completed successfully!")
