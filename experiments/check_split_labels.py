
from pathlib import Path
import pandas as pd

project = Path(__file__).resolve().parents[1]
folder = project / "data" / "processed"

splits = pd.read_csv(folder / "experiment_splits.csv")

for day in ["Monday", "Tuesday", "Wednesday"]:
    file = next(folder.glob(f"{day}*.csv"))

    labels = pd.read_csv(file, usecols=["Label"])

    selected = splits[
        splits["source_file"] == file.name
    ].copy()

    selected["Label"] = labels.iloc[
        selected["row_number"].to_numpy()
    ]["Label"].to_numpy()

    print(f"\n--- {day.upper()} ---")
    print(pd.crosstab(
        selected["split"],
        selected["Label"]
    ).to_string())
