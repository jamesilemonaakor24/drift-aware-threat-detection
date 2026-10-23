from pathlib import Path
import numpy as np
import pandas as pd

project = Path(__file__).resolve().parents[1]
folder = project / "data" / "processed"
rng = np.random.default_rng(2026)

# Reuse only rows that survived Experiment 1's leakage quarantine.
exp1 = pd.read_csv(folder / "experiment_splits.csv")
wed_file = next(folder.glob("Wednesday*.csv"))
wed_rows = exp1.loc[exp1["source_file"] == wed_file.name, "row_number"].to_numpy()

# Build float32 fingerprints exactly as the model sees the features.
df = pd.read_csv(wed_file)
feature_df = df.drop(columns=["Label", "attack_binary", "source_file"]).astype("float32")
features = feature_df.iloc[wed_rows]
fingerprints = pd.util.hash_pandas_object(features, index=False).to_numpy()

records = pd.DataFrame({
    "source_file": wed_file.name,
    "row_number": wed_rows,
    "fingerprint": fingerprints,
})

unique = records["fingerprint"].unique().copy()
rng.shuffle(unique)

n = len(unique)
seed_end = int(n * 0.20)
update_end = int(n * 0.70)

mapping = {}
for fp in unique[:seed_end]:
    mapping[fp] = "verified_seed_pool"
for fp in unique[seed_end:update_end]:
    mapping[fp] = "pseudo_update"
for fp in unique[update_end:]:
    mapping[fp] = "heldout_eval"

records["split"] = records["fingerprint"].map(mapping)

# Leakage guard.
leak = records.groupby("fingerprint")["split"].nunique()
assert leak.max() == 1, "Identical float32 fingerprints cross Experiment 2 groups."
assert set(records["split"].unique()) == {
    "verified_seed_pool", "pseudo_update", "heldout_eval"
}

out = folder / "experiment2_splits.csv"
records[["source_file", "row_number", "split"]].to_csv(out, index=False)

print("\n--- EXPERIMENT 2 GROUPS ---")
print(records["split"].value_counts().to_string())
print("\nFloat32 leakage check: PASS")
print(f"Saved: {out}")
