from pathlib import Path
import pandas as pd

project = Path(__file__).resolve().parents[1]
folder = project / "data" / "processed"

EXCLUDED = ["Label", "attack_binary", "source_file"]


def build_records(dtype=None):
    records = []

    for day in ["Monday", "Tuesday", "Wednesday"]:
        file = next(folder.glob(f"{day}*.csv"))
        print(f"Checking {day}...")

        df = pd.read_csv(file)
        features = df.drop(columns=EXCLUDED)

        if dtype is not None:
            features = features.astype(dtype)

        fingerprints = pd.util.hash_pandas_object(
            features,
            index=False
        )

        print(
            f"Duplicate feature rows within {day}: "
            f"{fingerprints.duplicated().sum():,}"
        )

        records.append(pd.DataFrame({
            "day": day,
            "fingerprint": fingerprints.to_numpy(),
            "label": df["Label"].to_numpy(),
            "binary": df["attack_binary"].to_numpy()
        }))

    return pd.concat(records, ignore_index=True)


def summarize(combined, heading):
    print(f"\n=== {heading} ===")

    day_counts = combined.groupby("fingerprint")["day"].nunique()
    shared = day_counts[day_counts > 1]

    label_counts = combined.groupby("fingerprint")["label"].nunique()
    label_conflicts = label_counts[label_counts > 1]

    binary_counts = combined.groupby("fingerprint")["binary"].nunique()
    binary_conflicts = binary_counts[binary_counts > 1]

    affected_binary = combined[
        combined["fingerprint"].isin(binary_conflicts.index)
    ]

    shared_rows = combined[
        combined["fingerprint"].isin(shared.index)
    ]

    union = set(shared.index) | set(binary_conflicts.index)
    quarantined_rows = combined[
        combined["fingerprint"].isin(union)
    ]

    print(f"Fingerprints shared between days: {len(shared):,}")
    print(f"Fingerprints with different original labels: {len(label_conflicts):,}")
    print(f"Fingerprints labelled both benign and attack: {len(binary_conflicts):,}")
    print(f"Rows in binary-conflicting groups: {len(affected_binary):,}")
    print(f"Rows in cross-day shared groups: {len(shared_rows):,}")
    print(
        "Rows in union of shared/conflicting groups: "
        f"{len(quarantined_rows):,}"
    )

    if len(affected_binary):
        print("\nBinary-conflict rows by day:")
        print(affected_binary["day"].value_counts().to_string())

        print("\nBinary-conflict rows by label:")
        print(affected_binary["label"].value_counts().to_string())


print("\n--- NATIVE-PRECISION FEATURE AUDIT ---")
native = build_records(dtype=None)
summarize(native, "NATIVE PRECISION")

print(
    "\n--- MODEL-VISIBLE FLOAT32 FEATURE AUDIT ---\n"
    "This second pass matches the numeric representation used by the models "
    "and by create_splits.py."
)
float32 = build_records(dtype="float32")
summarize(float32, "FLOAT32 MODEL INPUTS")
