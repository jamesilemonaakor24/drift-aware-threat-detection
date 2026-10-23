from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

project = Path(__file__).resolve().parents[1]
folder = project / "data" / "processed"
artifacts = project / "experiments" / "artifacts"

base_saved = joblib.load(artifacts / "experiment2_adapted_baseline.joblib")
cand_saved = joblib.load(artifacts / "experiment2_candidate.joblib")
base = base_saved["model"]
candidate = cand_saved["model"]
features = base_saved["features"]
assert features == cand_saved["features"]

exp2 = pd.read_csv(folder / "experiment2_splits.csv")
wed_file = next(folder.glob("Wednesday*.csv"))
full = pd.read_csv(wed_file)

# Held-out evaluation for Experiment 2.
eval_rows = exp2.loc[exp2["split"] == "heldout_eval", "row_number"].to_numpy()
eval_df = full.iloc[eval_rows].copy().reset_index(drop=True)
X = eval_df[features].astype("float32")
y = eval_df["attack_binary"].astype(int)

print(f"\nHeld-out Experiment 2 records: {len(eval_df):,}")
print(f"Benign: {(y == 0).sum():,}")
print(f"Attack: {(y == 1).sum():,}")

def examine(model, name):
    pred = model.predict(X)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    fpr = fp / (fp + tn) if (fp + tn) else np.nan
    recall = tp / (tp + fn) if (tp + fn) else np.nan

    print(f"\n--- {name} ---")
    print(f"False alarms: {fp:,}")
    print(f"Missed attacks: {fn:,}")
    print(f"Attacks detected: {tp:,}")
    print(f"False Positive Rate: {fpr:.4%}")
    print(f"Attack Recall: {recall:.2%}")

    print("Attack classes:")
    for label in sorted(eval_df.loc[eval_df["attack_binary"] == 1, "Label"].unique()):
        mask = eval_df["Label"] == label
        total = int(mask.sum())
        detected = int((pred[mask] == 1).sum())
        print(f"{label}: {detected:,}/{total:,} ({detected/total:.2%})")
    return fpr, recall

base_fpr, base_recall = examine(base, "ADAPTED BASELINE")
cand_fpr, cand_recall = examine(candidate, "PSEUDO-UPDATED CANDIDATE")

fpr_increase = cand_fpr - base_fpr
recall_drop = base_recall - cand_recall

print("\n--- COMPARISON ---")
print(f"FPR change: {fpr_increase * 100:+.4f} percentage points")
print(f"Recall change: {(cand_recall - base_recall) * 100:+.2f} percentage points")

harmful = (fpr_increase > 0.001) or (recall_drop > 0.05)
print("\n--- PREDEFINED VERDICT ---")
print("HARMFUL" if harmful else "NOT HARMFUL under the predefined limits")

# Only now reveal labels of the pseudo-update examples selected during training.
selected_rows = cand_saved["selected_source_rows"]
selected_truth = full.loc[selected_rows, ["Label", "attack_binary"]].copy()
attacks = selected_truth[selected_truth["attack_binary"] == 1]

print("\n--- PSEUDO-UPDATE CONTAMINATION ---")
print(f"Selected pseudo-benign flows: {len(selected_truth):,}")
print(f"Actually attacks: {len(attacks):,}")
print(f"Contamination rate: {len(attacks)/len(selected_truth):.2%}")
if len(attacks):
    print("Attack classes mislabeled as benign:")
    print(attacks["Label"].value_counts().to_string())

print("\nInterpretation note:")
print("This is an exploratory held-out follow-up, not a new project-level blind confirmation, because Wednesday labels were already examined in Experiment 1.")
