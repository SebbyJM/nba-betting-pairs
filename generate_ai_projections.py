import pandas as pd

# Load L10 & H2H Data
l10_h2h_points = pd.read_csv("Player_Points_L10_H2H.csv")
l10_h2h_rebounds = pd.read_csv("Player_Rebounds_L10_H2H.csv")
l10_h2h_assists = pd.read_csv("Player_Assists_L10_H2H.csv")

# Function to calculate AI projection
def calculate_projection(df, l10_col, h2h_col, category):
    df["AI_Projection"] = (df[l10_col] * 0.6) + (df[h2h_col] * 0.4)  # 60% L10 + 40% H2H
    df["Category"] = category  # Add Category column
    return df[["Player", "AI_Projection", "Category"]]

# Generate AI projections
ai_points = calculate_projection(l10_h2h_points, "L10_PTS", "H2H_PTS", "Points")
ai_rebounds = calculate_projection(l10_h2h_rebounds, "L10_REB", "H2H_REB", "Rebounds")
ai_assists = calculate_projection(l10_h2h_assists, "L10_AST", "H2H_AST", "Assists")

# Save AI projections
ai_points.to_csv("AI_Projections_POINTS.csv", index=False)
ai_rebounds.to_csv("AI_Projections_REBOUNDS.csv", index=False)
ai_assists.to_csv("AI_Projections_ASSISTS.csv", index=False)

print("✅ AI projections successfully generated!")