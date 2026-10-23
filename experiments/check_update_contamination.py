from pathlib import Path
import joblib
import numpy as np
import pandas as pd

project = Path(__file__).resolve().parents[1]
folder = project / "data" / "processed"
artifacts = project / "experiments" / "artifacts"

saved = joblib.load(
    artifacts / "baseline_random_forest.joblib"
)

original = saved["model"]
features = saved["features"]

splits = pd.read_csv(
    folder / "experiment_splits.csv"
)

file = next(folder.glob("Wednesday*.csv"))

rows = splits.loc[
    (splits["source_file"] == file.name)
    & (splits["split"] == "update"),
    "row_number"
].to_numpy()

# Reconstruct exactly what train_candidate.py saw
features_only = pd.read_csv(
    file,
    usecols=features
)

X_update = (
    features_only
    .iloc[rows][features]
    .astype("float32")
)

probabilities = original.predict_proba(X_update)

benign_index = list(original.classes_).index(0)
benign_confidence = probabilities[:, benign_index]

eligible = np.flatnonzero(
    benign_confidence >= 0.99
)

# Same random selection used during candidate training
rng = np.random.default_rng(42)

selected = rng.choice(
    eligible,
    size=min(20000, len(eligible)),
    replace=False
)

# NOW open the true-label answer sheet
truth = pd.read_csv(
    file,
    usecols=["Label", "attack_binary"]
).iloc[rows].reset_index(drop=True)

selected_truth = truth.iloc[selected]

attacks = selected_truth[
    selected_truth["attack_binary"] == 1
]

benign = selected_truth[
    selected_truth["attack_binary"] == 0
]

print("\n--- UPDATE CONTAMINATION CHECK ---")
print(f"Selected pseudo-benign flows: {len(selected_truth):,}")
print(f"Actually benign: {len(benign):,}")
print(f"Actually attacks: {len(attacks):,}")

rate = len(attacks) / len(selected_truth)

print(f"Contamination rate: {rate:.2%}")

print("\nAttack classes incorrectly taught as benign:")

if len(attacks) == 0:
    print("None")
else:
    print(
        attacks["Label"]
        .value_counts()
        .to_string()
    )

print("\nNo models were changed.")
print("Blind-test data was NOT used.")