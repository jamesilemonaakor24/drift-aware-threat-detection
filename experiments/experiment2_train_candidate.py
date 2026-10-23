from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone

project = Path(__file__).resolve().parents[1]
folder = project / "data" / "processed"
artifacts = project / "experiments" / "artifacts"

adapted_saved = joblib.load(artifacts / "experiment2_adapted_baseline.joblib")
adapted = adapted_saved["model"]
features = adapted_saved["features"]

# Reconstruct original Monday/Tuesday training data.
exp1 = pd.read_csv(folder / "experiment_splits.csv")
old_parts = []
for day in ["Monday", "Tuesday"]:
    file = next(folder.glob(f"{day}*.csv"))
    rows = exp1.loc[
        (exp1["source_file"] == file.name) & (exp1["split"] == "training"),
        "row_number"
    ].to_numpy()
    df = pd.read_csv(file, usecols=features + ["attack_binary"])
    old_parts.append(df.iloc[rows].copy())
old = pd.concat(old_parts, ignore_index=True)

# Reconstruct exact verified seed selected in the baseline step.
wed_file = next(folder.glob("Wednesday*.csv"))
wed_features_labels = pd.read_csv(wed_file, usecols=features + ["attack_binary"])
verified_rows = adapted_saved["verified_seed_rows"]
verified = wed_features_labels.loc[verified_rows].copy()

# Load pseudo-update features ONLY. Do not read true labels here.
exp2 = pd.read_csv(folder / "experiment2_splits.csv")
update_rows = exp2.loc[exp2["split"] == "pseudo_update", "row_number"].to_numpy()
features_only = pd.read_csv(wed_file, usecols=features)
X_update = features_only.iloc[update_rows][features].astype("float32")

prob = adapted.predict_proba(X_update)
benign_index = list(adapted.classes_).index(0)
benign_conf = prob[:, benign_index]
eligible = np.flatnonzero(benign_conf >= 0.99)

print(f"Pseudo-update flows: {len(X_update):,}")
print(f"High-confidence benign predictions: {len(eligible):,}")

rng = np.random.default_rng(2026)
selected_pos = rng.choice(
    eligible,
    size=min(20000, len(eligible)),
    replace=False
)
if len(selected_pos) == 0:
    raise RuntimeError("No >=99% benign-confidence update examples found.")

selected_source_rows = update_rows[selected_pos]
X_new = X_update.iloc[selected_pos].copy()
y_new = pd.Series(np.zeros(len(X_new), dtype=int))

X_old = old[features].astype("float32")
y_old = old["attack_binary"].astype(int)
X_seed = verified[features].astype("float32")
y_seed = verified["attack_binary"].astype(int)

X = pd.concat([X_old, X_seed, X_new], ignore_index=True)
y = pd.concat([y_old, y_seed, y_new], ignore_index=True)

candidate = clone(adapted)
print(f"Selected for pseudo-update: {len(X_new):,}")
print("Training Experiment 2 candidate...")
candidate.fit(X, y)

joblib.dump({
    "model": candidate,
    "features": features,
    "selected_source_rows": selected_source_rows,
    "confidence_threshold": 0.99,
    "pseudo_benign_count": len(X_new),
}, artifacts / "experiment2_candidate.joblib")

print("SUCCESS: Experiment 2 candidate saved.")
print("True pseudo-update labels were NOT used for training.")
print("Held-out evaluation data was NOT used.")
