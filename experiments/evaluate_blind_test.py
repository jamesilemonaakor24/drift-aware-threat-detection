from pathlib import Path
import pandas as pd
import joblib
from sklearn.metrics import confusion_matrix

project = Path(__file__).resolve().parents[1]
folder = project / "data" / "processed"
artifacts = project / "experiments" / "artifacts"

original = joblib.load(
    artifacts / "baseline_random_forest.joblib"
)

candidate = joblib.load(
    artifacts / "candidate_01.joblib"
)

features = original["features"]

splits = pd.read_csv(
    folder / "experiment_splits.csv"
)

file = next(folder.glob("Wednesday*.csv"))

rows = splits.loc[
    (splits["source_file"] == file.name)
    & (splits["split"] == "blind_test"),
    "row_number"
].to_numpy()

df = pd.read_csv(file)

blind = df.iloc[rows].copy().reset_index(drop=True)

X = blind[features].astype("float32")
y = blind["attack_binary"]

print(f"\nBlind test records: {len(blind):,}")

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
    print(f"Unseen Attack Recall: {recall:.2%}")

    print("\nAttack classes:")

    for label in sorted(
        blind.loc[blind["attack_binary"] == 1, "Label"].unique()
    ):
        mask = blind["Label"] == label

        total = mask.sum()
        detected = (predictions[mask] == 1).sum()

        print(
            f"{label}: {detected:,}/{total:,} "
            f"({detected / total:.2%})"
        )

    return fpr, recall


old_fpr, old_recall = examine(
    original["model"],
    "ORIGINAL GUARD"
)

new_fpr, new_recall = examine(
    candidate["model"],
    "UPDATED GUARD"
)

fpr_increase = new_fpr - old_fpr
recall_drop = old_recall - new_recall

print("\n--- BLIND COMPARISON ---")
print(
    f"FPR change: "
    f"{fpr_increase * 100:+.4f} percentage points"
)

print(
    f"Unseen recall change: "
    f"{(new_recall - old_recall) * 100:+.2f} percentage points"
)

# Predefined limits
harmful = (
    fpr_increase > 0.001
    or recall_drop > 0.05
)

print("\n--- FINAL BLIND VERDICT ---")

if harmful:
    print("Candidate is HARMFUL under the predefined limits.")
else:
    print("Candidate is NOT more harmful than the baseline under the predefined comparative limits.")

print("\n--- INTERPRETATION NOTE ---")
print(
    "This is a relative comparison with the frozen baseline. "
    "It does not mean either model is safe or effective on Wednesday traffic."
)
if old_recall == 0 and new_recall == 0:
    print(
        "Both models have 0% unseen-attack recall. "
        "This creates a floor effect, so the candidate cannot show a further recall drop."
    )
    print(
        "Experiment 1 is therefore inconclusive for the harmful-update hypothesis."
    )

print("\nNo models were changed.")