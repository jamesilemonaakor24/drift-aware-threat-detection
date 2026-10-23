
from pathlib import Path
import pandas as pd

# Find the cleaned dataset
project = Path(__file__).resolve().parents[1]
data_folder = project / "data" / "processed"

# Check the attack types on each day
for day in ["Monday", "Tuesday", "Wednesday"]:
    files = list(data_folder.glob(f"{day}*.csv"))

    if not files:
        print(f"No file found for {day}")
        continue

    df = pd.read_csv(files[0], usecols=["Label"])

    print(f"\n--- {day.upper()} ---")
    print(f"Total flows: {len(df):,}")
    print(df["Label"].value_counts().to_string())
