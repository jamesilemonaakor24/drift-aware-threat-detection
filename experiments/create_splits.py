
from pathlib import Path
import numpy as np
import pandas as pd

# =====================================
# 1. FIND OUR DATASET
# =====================================

project = Path(__file__).resolve().parents[1]
folder = project / "data" / "processed"

rng = np.random.default_rng(42)

all_days = []

# =====================================
# 2. READ MONDAY, TUESDAY, WEDNESDAY
# =====================================

for day in ["Monday", "Tuesday", "Wednesday"]:

    files = list(folder.glob(f"{day}*.csv"))

    if len(files) != 1:
        raise FileNotFoundError(
            f"Expected one processed CSV for {day}, "
            f"but found {len(files)}"
        )

    file = files[0]

    print(f"Reading {day}...")

    df = pd.read_csv(file)

    # Keep only network features for fingerprints
    features = df.drop(
    columns=["Label", "attack_binary", "source_file"]
).astype("float32")

    fingerprints = pd.util.hash_pandas_object(
        features,
        index=False
    )

    records = pd.DataFrame({
        "day": day,
        "source_file": file.name,
        "row_number": np.arange(len(df)),
        "fingerprint": fingerprints.to_numpy(),
        "binary": df["attack_binary"].to_numpy()
    })

    all_days.append(records)

combined = pd.concat(all_days, ignore_index=True)

print(f"\nOriginal records: {len(combined):,}")

# =====================================
# 3. QUARANTINE PROBLEMATIC FINGERPRINTS
# =====================================

# Same features with different binary labels
label_counts = combined.groupby(
    "fingerprint"
)["binary"].nunique()

conflicts = set(
    label_counts[label_counts > 1].index
)

# Same features appearing on different days
day_counts = combined.groupby(
    "fingerprint"
)["day"].nunique()

shared = set(
    day_counts[day_counts > 1].index
)

# Quarantine both types.
# NOTE: these fingerprints were created from float32 features, matching
# the numeric representation used by the models. This is intentionally
# stricter than the earlier native-precision duplicate audit.
excluded = conflicts | shared

conflict_rows = combined["fingerprint"].isin(conflicts)
shared_rows = combined["fingerprint"].isin(shared)
excluded_rows = combined["fingerprint"].isin(excluded)

clean = combined[~excluded_rows].copy()

print(f"Conflicting float32 fingerprints: {len(conflicts):,}")
print(f"Rows in conflicting float32 groups: {int(conflict_rows.sum()):,}")
print(f"Cross-day shared float32 fingerprints: {len(shared):,}")
print(f"Rows in cross-day shared float32 groups: {int(shared_rows.sum()):,}")
print(
    "Quarantined records (union; overlap counted once): "
    f"{int(excluded_rows.sum()):,}"
)

# =====================================
# 4. CREATE EXPERIMENT GROUPS
# =====================================

parts = []

for day in ["Monday", "Tuesday", "Wednesday"]:

    subset = clean[
        clean["day"] == day
    ].copy()

    # Keep matching feature patterns together
    unique = subset["fingerprint"].unique().copy()

    rng.shuffle(unique)

    n = len(unique)

    if day == "Wednesday":

        # Wednesday is our newer traffic
        update_end = int(n * 0.60)
        audit_end = int(n * 0.80)

        labels = (
            ["update"] * update_end
            + ["recent_audit"] * (audit_end - update_end)
            + ["blind_test"] * (n - audit_end)
        )

    else:

        # Monday and Tuesday are earlier traffic
        train_end = int(n * 0.70)
        audit_end = int(n * 0.90)

        labels = (
            ["training"] * train_end
            + ["old_audit"] * (audit_end - train_end)
            + ["known_test"] * (n - audit_end)
        )

    mapping = dict(zip(unique, labels))

    subset["split"] = subset[
        "fingerprint"
    ].map(mapping)

    parts.append(subset)

result = pd.concat(parts, ignore_index=True)

# =====================================
# 5. CHECK FOR DATA LEAKAGE
# =====================================

leakage = result.groupby(
    "fingerprint"
)["split"].nunique()

assert leakage.max() == 1, (
    "ERROR: Identical fingerprints appear "
    "in different experiment groups!"
)

# Confirm the correct days were assigned
early_groups = {"training", "old_audit", "known_test"}
new_groups = {"update", "recent_audit", "blind_test"}

assert set(
    result.loc[
        result["day"].isin(["Monday", "Tuesday"]),
        "split"
    ]
).issubset(early_groups)

assert set(
    result.loc[
        result["day"] == "Wednesday",
        "split"
    ]
).issubset(new_groups)

assert result["split"].nunique() == 6, (
    "ERROR: Expected six experiment groups!"
)

# =====================================
# 6. SAVE EXPERIMENT SPLITS
# =====================================

output = folder / "experiment_splits.csv"

result[
    ["source_file", "row_number", "split"]
].to_csv(output, index=False)

# =====================================
# 7. DISPLAY RESULTS
# =====================================

print("\n--- EXPERIMENT GROUPS ---")

print(
    result["split"]
    .value_counts()
    .to_string()
)

print("\n--- GROUPS BY DAY ---")

print(
    pd.crosstab(
        result["day"],
        result["split"]
    ).to_string()
)

print("\nLeakage check: PASS")

print(f"Split file saved: {output}")
