from pathlib import Path
import pandas as pd
import joblib

project = Path(__file__).resolve().parents[1]
folder = project / "data" / "processed"
artifacts = project / "experiments" / "artifacts"

# Use exactly the same features our security guard uses
saved = joblib.load(
    artifacts / "baseline_random_forest.joblib"
)

features = saved["features"]

# Load the existing experiment assignments
splits = pd.read_csv(
    folder / "experiment_splits.csv"
)

records = []

for day in ["Monday", "Tuesday", "Wednesday"]:

    file = next(folder.glob(f"{day}*.csv"))

    print(f"Checking {day}...")

    assignments = splits[
        splits["source_file"] == file.name
    ].copy()

    # Read only the model's features
    df = pd.read_csv(
        file,
        usecols=features
    )

    rows = assignments["row_number"].to_numpy()

    # EXACT numeric format seen by the models
    X = df.iloc[rows][features].astype("float32")

    fingerprints = pd.util.hash_pandas_object(
        X,
        index=False
    )

    records.append(
        pd.DataFrame({
            "fingerprint": fingerprints.to_numpy(),
            "split": assignments["split"].to_numpy()
        })
    )

combined = pd.concat(records, ignore_index=True)

# Does one model-visible fingerprint appear
# in more than one experiment group?
overlap = combined.groupby(
    "fingerprint"
)["split"].nunique()

leaks = overlap[overlap > 1]

print("\n--- FLOAT32 LEAKAGE CHECK ---")
print(f"Cross-split fingerprints: {len(leaks):,}")

if len(leaks) == 0:
    print("RESULT: PASS")
    print("No identical float32 model inputs cross experiment groups.")
else:
    print("RESULT: WARNING")
    print("Identical float32 model inputs appear in different groups.")

    affected = combined[
        combined["fingerprint"].isin(leaks.index)
    ]

    print("\nAffected rows by split:")
    print(
        affected["split"]
        .value_counts()
        .to_string()
    )