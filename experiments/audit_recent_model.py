
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import confusion_matrix

# Find project files
project = Path(__file__).resolve().parents[1]
folder = project / "data" / "processed"
artifacts = project / "experiments" / "artifacts"

# Load both security guards
original = joblib.load(
    artifacts / "baseline_random_forest.joblib"
)
candidate = joblib.load(
    artifacts / "candidate_01.joblib"
)

features = original["features"]
assert features == candidate["features"]

# Load experiment groups
splits = pd.read_csv(
    folder / "experiment_splits.csv"
)

file = next(folder.glob("Wednesday*.csv"))

rows = splits.loc[
    (splits["source_file"] == file.name)
    & (splits["split"] == "recent_audit"),
    "row_number"
].to_numpy()

# Fixed random selection: 200 records
rng = np.random.default_rng(42)

selected_rows = rng.choice(
    rows,
    size=200,
    replace=False
)

# Read only the selected audit records
df = pd.read_csv(file)
audit = df.iloc[selected_rows].copy()

X = audit[features].astype("float32")
y = audit["attack_binary"]

print("\n--- RECENT SAFETY EXAMINATION ---")
print(f"Records examined: {len(audit)}")
print(f"Normal records: {(y == 0).sum()}")
print(f"Attack records: {(y == 1).sum()}")

def examine(model, name):
    predictions = model.predict(X)

    tn, fp, fn, tp = confusion_matrix(
        y, predictions, labels=[0, 1]
    ).ravel()

    fpr = fp / (fp + tn) if (fp + tn) else np.nan
    recall = tp / (tp + fn) if (tp + fn) else np.nan

    print(f"\n--- {name} ---")
    print(f"False alarms: {fp}")
    print(f"Missed attacks: {fn}")
    print(f"Attacks detected: {tp}")
    print(f"False Positive Rate: {fpr:.4%}")
    print(f"Attack Recall: {recall:.2%}")

    return fpr, recall

old_fpr, old_recall = examine(
    original["model"], "ORIGINAL GUARD"
)

new_fpr, new_recall = examine(
    candidate["model"], "UPDATED GUARD"
)

print("\n--- EXPLORATORY COMPARISON ---")

if np.isfinite(old_fpr) and np.isfinite(new_fpr):
    print(
        "FPR change:",
        f"{(new_fpr - old_fpr) * 100:+.4f}",
        "percentage points"
    )

if np.isfinite(old_recall) and np.isfinite(new_recall):
    print(
        "Recall change:",
        f"{(new_recall - old_recall) * 100:+.2f}",
        "percentage points"
    )

print("\nNo final safety decision made.")
print("Wednesday blind test was NOT used.")
