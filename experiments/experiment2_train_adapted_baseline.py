from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone

project = Path(__file__).resolve().parents[1]
folder = project / "data" / "processed"
artifacts = project / "experiments" / "artifacts"
artifacts.mkdir(parents=True, exist_ok=True)

# Load original baseline to preserve the exact feature list and RF architecture.
saved = joblib.load(artifacts / "baseline_random_forest.joblib")
original = saved["model"]
features = saved["features"]

exp1 = pd.read_csv(folder / "experiment_splits.csv")
exp2 = pd.read_csv(folder / "experiment2_splits.csv")

# Original Monday/Tuesday training data.
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

# Verified Wednesday seed pool. These labels are intentionally allowed here.
wed_file = next(folder.glob("Wednesday*.csv"))
seed_rows = exp2.loc[exp2["split"] == "verified_seed_pool", "row_number"].to_numpy()
wed = pd.read_csv(wed_file, usecols=features + ["Label", "attack_binary"])
seed_pool = wed.iloc[seed_rows].copy()

rng = np.random.default_rng(2026)
benign_idx = seed_pool.index[seed_pool["attack_binary"] == 0].to_numpy()
attack_idx = seed_pool.index[seed_pool["attack_binary"] == 1].to_numpy()

n_benign = min(2000, len(benign_idx))
n_attack = min(2000, len(attack_idx))

chosen_benign = rng.choice(benign_idx, size=n_benign, replace=False)
chosen_attack = rng.choice(attack_idx, size=n_attack, replace=False)
chosen_index = np.concatenate([chosen_benign, chosen_attack])
rng.shuffle(chosen_index)

verified = seed_pool.loc[chosen_index].copy()

print("\n--- VERIFIED ADAPTATION SEED ---")
print(f"Benign: {(verified['attack_binary'] == 0).sum():,}")
print(f"Attack: {(verified['attack_binary'] == 1).sum():,}")
print("Attack classes:")
if (verified["attack_binary"] == 1).any():
    print(verified.loc[verified["attack_binary"] == 1, "Label"].value_counts().to_string())

X_old = old[features].astype("float32")
y_old = old["attack_binary"].astype(int)
X_seed = verified[features].astype("float32")
y_seed = verified["attack_binary"].astype(int)

X = pd.concat([X_old, X_seed], ignore_index=True)
y = pd.concat([y_old, y_seed], ignore_index=True)

adapted = clone(original)
print(f"\nTraining adapted baseline on {len(X):,} records...")
adapted.fit(X, y)

joblib.dump({
    "model": adapted,
    "features": features,
    "verified_seed_rows": verified.index.to_numpy(),
    "verified_benign": int((verified["attack_binary"] == 0).sum()),
    "verified_attacks": int((verified["attack_binary"] == 1).sum()),
}, artifacts / "experiment2_adapted_baseline.joblib")

print("SUCCESS: Experiment 2 adapted baseline saved.")
print("Pseudo-update and held-out evaluation groups were not used for training.")
