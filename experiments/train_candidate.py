
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone

# 1. Locate project files
project = Path(__file__).resolve().parents[1]
folder = project / "data" / "processed"
artifacts = project / "experiments" / "artifacts"

# 2. Load original security guard
saved = joblib.load(
    artifacts / "baseline_random_forest.joblib"
)

original = saved["model"]
features = saved["features"]

splits = pd.read_csv(
    folder / "experiment_splits.csv"
)

# 3. Load original training examples
training_parts = []

for day in ["Monday", "Tuesday"]:
    file = next(folder.glob(f"{day}*.csv"))

    rows = splits.loc[
        (splits["source_file"] == file.name)
        & (splits["split"] == "training"),
        "row_number"
    ].to_numpy()

    df = pd.read_csv(
        file,
        usecols=features + ["attack_binary"]
    )

    training_parts.append(df.iloc[rows].copy())

train = pd.concat(training_parts, ignore_index=True)

X_old = train[features].astype("float32")
y_old = train["attack_binary"]

# 4. Load Wednesday update traffic
file = next(folder.glob("Wednesday*.csv"))

rows = splits.loc[
    (splits["source_file"] == file.name)
    & (splits["split"] == "update"),
    "row_number"
].to_numpy()

# Do NOT read Wednesday's true labels
wednesday = pd.read_csv(file, usecols=features)
X_update = wednesday.iloc[rows][features].astype("float32")

# 5. Select traffic the original model
# is at least 99% confident is BENIGN
probabilities = original.predict_proba(X_update)

benign_index = list(original.classes_).index(0)
benign_confidence = probabilities[:, benign_index]

eligible = np.flatnonzero(benign_confidence >= 0.99)

print(f"Wednesday update flows: {len(X_update):,}")
print(f"High-confidence benign predictions: {len(eligible):,}")

# Experimental choice: use up to 20,000 flows
rng = np.random.default_rng(42)

selected = rng.choice(
    eligible,
    size=min(20000, len(eligible)),
    replace=False
)

if len(selected) == 0:
    raise RuntimeError("No suitable update examples found.")

X_new = X_update.iloc[selected].copy()

# These are predictions, NOT verified labels
y_new = pd.Series(
    np.zeros(len(X_new), dtype=int)
)

print(f"Selected for update: {len(X_new):,}")

# 6. Combine original and new examples
X_train = pd.concat(
    [X_old, X_new],
    ignore_index=True
)

y_train = pd.concat(
    [y_old, y_new],
    ignore_index=True
)

# 7. Train updated version of same model
candidate = clone(original)

print("\nTraining updated security guard...")
candidate.fit(X_train, y_train)

# 8. Save without replacing original model
joblib.dump(
    {
        "model": candidate,
        "features": features,
        "pseudo_benign_count": len(X_new),
        "confidence_threshold": 0.99
    },
    artifacts / "candidate_01.joblib"
)

print("\nSUCCESS: Candidate update saved!")
print("Original model remains unchanged.")
print("No Wednesday true labels were used.")
print("No safety audit or blind test was performed.")
