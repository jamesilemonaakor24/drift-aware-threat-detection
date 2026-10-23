
from pathlib import Path
import pandas as pd
import joblib
from sklearn.metrics import confusion_matrix

# Locate project files
project = Path(__file__).resolve().parents[1]
folder = project / "data" / "processed"
artifacts = project / "experiments" / "artifacts"

# Load both guards
original = joblib.load(
    artifacts / "baseline_random_forest.joblib"
)

candidate = joblib.load(
    artifacts / "candidate_01.joblib"
)

features = original["features"]

assert features == candidate["features"]

# Load saved experiment groups
splits = pd.read_csv(
    folder / "experiment_splits.csv"
)

parts = []

# OLD AUDIT: Monday and Tuesday only
for day in ["Monday", "Tuesday"]:
    file = next(folder.glob(f"{day}*.csv"))

    rows = splits.loc[
        (splits["source_file"] == file.name)
        & (splits["split"] == "old_audit"),
        "row_number"
    ].to_numpy()

    df = pd.read_csv(file)
    parts.append(df.iloc[rows].copy())

audit = pd.concat(parts, ignore_index=True)

X = audit[features].astype("float32")
y = audit["attack_binary"]

def examine(model, name):
    predictions = model.predict(X)

    tn, fp, fn, tp = confusion_matrix(
        y, predictions, labels=[0, 1]
    ).ravel()

    fpr = fp / (fp + tn)
    recall = tp / (tp + fn)

    print(f"\n--- {name} ---")
    print(f"False alarms: {fp:,}")
    print(f"Missed attacks: {fn:,}")
    print(f"Attacks detected: {tp:,}")
    print(f"False Positive Rate: {fpr:.4%}")
    print(f"Attack Recall: {recall:.2%}")

    return fpr, recall

print(f"\nOld audit records: {len(audit):,}")

old_fpr, old_recall = examine(
    original["model"], "ORIGINAL GUARD"
)

new_fpr, new_recall = examine(
    candidate["model"], "UPDATED GUARD"
)

# Predefined safety limits
MAX_FPR_INCREASE = 0.001
MAX_RECALL_DROP = 0.05

fpr_increase = new_fpr - old_fpr
recall_drop = old_recall - new_recall

approved = (
    fpr_increase <= MAX_FPR_INCREASE
    and recall_drop <= MAX_RECALL_DROP
)

print("\n--- OLD SAFETY AUDIT DECISION ---")
print(f"FPR change: {fpr_increase * 100:+.4f} percentage points")
print(f"Recall change: {-recall_drop * 100:+.2f} percentage points")

if approved:
    print("DECISION: APPROVED RELATIVE TO BASELINE")
else:
    print("DECISION: REJECTED")

print("\nApproval here is comparative only; it is not an absolute safety guarantee.")
print("Wednesday blind test was NOT used.")
print("No model files were changed.")
