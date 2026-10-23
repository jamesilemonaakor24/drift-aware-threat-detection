
from pathlib import Path
import pandas as pd
import joblib

from sklearn.metrics import (
    confusion_matrix,
    classification_report
)

# Find project files
project = Path(__file__).resolve().parents[1]
folder = project / "data" / "processed"

# Load our trained security guard
saved = joblib.load(
    project / "experiments" / "artifacts"
    / "baseline_random_forest.joblib"
)

model = saved["model"]
features = saved["features"]

# Load experiment groups
splits = pd.read_csv(
    folder / "experiment_splits.csv"
)

test_data = []

# Use ONLY Monday and Tuesday known_test records
for day in ["Monday", "Tuesday"]:
    file = next(folder.glob(f"{day}*.csv"))

    rows = splits.loc[
        (splits["source_file"] == file.name)
        & (splits["split"] == "known_test"),
        "row_number"
    ].to_numpy()

    df = pd.read_csv(file)
    test_data.append(df.iloc[rows].copy())

test = pd.concat(test_data, ignore_index=True)

# Separate features from correct answers
X = test[features].astype("float32")
y = test["attack_binary"]

# Ask our guard to make predictions
predictions = model.predict(X)

print("\n--- BASELINE MODEL EXAMINATION ---")
print(f"Test records: {len(test):,}")

print("\nClassification Report:")
print(
    classification_report(
        y,
        predictions,
        labels=[0, 1],
        target_names=["Normal", "Attack"],
        zero_division=0
    )
)

# Count correct and incorrect decisions
tn, fp, fn, tp = confusion_matrix(
    y, predictions, labels=[0, 1]
).ravel()

print("\n--- SECURITY RESULTS ---")
print(f"Normal traffic correctly recognised: {tn:,}")
print(f"False alarms (FP): {fp:,}")
print(f"Missed attacks (FN): {fn:,}")
print(f"Attacks correctly detected: {tp:,}")

# Percentage of normal traffic wrongly flagged
fpr = fp / (fp + tn) if (fp + tn) else 0

print(f"\nFalse Positive Rate: {fpr:.4%}")

# Examine each known attack separately
print("\n--- KNOWN ATTACK DETECTION ---")

for attack in ["FTP - Patator", "SSH - Patator"]:
    mask = test["Label"] == attack

    total = int(mask.sum())
    detected = int((predictions[mask] == 1).sum())

    recall = detected / total if total else 0

    print(
        f"{attack}: {detected:,}/{total:,} "
        f"detected ({recall:.2%})"
    )

print("\nWednesday blind data was NOT used.")
