import pandas as pd
import os

# List of files to process
files = ["NBA STATS - POINTS.csv", "NBA STATS - ASSISTS.csv", "NBA STATS - REBOUNDS.csv"]

# Function to process each file
def process_file(file_path):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    # Load the CSV file with manual column names
    df = pd.read_csv(file_path, names=["label", "description", "price", "point"], header=None)

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()

    # Ensure price and point columns are numeric
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["point"] = pd.to_numeric(df["point"], errors="coerce")

    # Function to extract the best odds
    def get_best_odds(group):
        best_over = group[group["label"] == "Over"].nsmallest(1, "price")  # Most negative Over odds
        best_under = group[group["label"] == "Under"]
        best_under = best_under.loc[best_under["price"].abs().idxmin()] if not best_under.empty else None  # Closest to 0 Under odds

        return pd.DataFrame({
            "Player": [group["description"].iloc[0]],
            "Best_Over_Odds": [best_over["price"].values[0] if not best_over.empty else None],
            "Best_Under_Odds": [best_under["price"] if best_under is not None else None],
            "Best_Point": [group["point"].iloc[0]]
        })

    # Apply function to group by player
    cleaned_df = df.groupby("description", group_keys=False).apply(get_best_odds).reset_index(drop=True)

    # Save decimals for the line ("Best_Point")
    cleaned_df["Best_Over_Odds"] = cleaned_df["Best_Over_Odds"].apply(lambda x: str(int(x)) if pd.notna(x) and x % 1 == 0 else str(x))
    cleaned_df["Best_Under_Odds"] = cleaned_df["Best_Under_Odds"].apply(lambda x: str(int(x)) if pd.notna(x) and x % 1 == 0 else str(x))
    cleaned_df["Best_Point"] = cleaned_df["Best_Point"].map(lambda x: f"{x:.1f}" if pd.notna(x) else "")

    # Generate output file name dynamically
    output_file = f"Cleaned_Best_Odds_{file_path.replace('NBA STATS - ', '').replace('.csv', '')}.csv"
    cleaned_df.to_csv(output_file, index=False)

    print(f"✅ Cleaned file saved as: {output_file}")

# Process all files in the list
for file in files:
    process_file(file)

print("✅ All files processed successfully!")
