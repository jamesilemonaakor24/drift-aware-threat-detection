import pandas as pd
import numpy as np
from pathlib import Path


# ---------------------------------------------------------
# 1. Define input and output directories
# ---------------------------------------------------------

raw_folder = Path("data/raw/MachineLearningCVE")
processed_folder = Path("data/processed")

processed_folder.mkdir(parents=True, exist_ok=True)

csv_files = sorted(raw_folder.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {raw_folder}")

print(f"Files to preprocess: {len(csv_files)}")


# ---------------------------------------------------------
# 2. Process each file independently
# ---------------------------------------------------------

total_before = 0
total_after = 0
total_removed_nonfinite = 0

for file_path in csv_files:

    print("\n" + "=" * 90)
    print("Processing:", file_path.name)

    df = pd.read_csv(file_path)

    rows_before = len(df)
    total_before += rows_before


    # -----------------------------------------------------
    # 3. Clean column names
    # -----------------------------------------------------

    df.columns = df.columns.str.strip()


    # -----------------------------------------------------
    # 4. Standardize labels
    # -----------------------------------------------------

    df["Label"] = df["Label"].astype(str).str.strip()

    df["Label"] = (
        df["Label"]
        .str.replace("�", "-", regex=False)
        .str.replace(r"\s*-\s*", " - ", regex=True)
    )


    # -----------------------------------------------------
    # 5. Replace infinity with NaN
    # -----------------------------------------------------

    df.replace([np.inf, -np.inf], np.nan, inplace=True)


    # -----------------------------------------------------
    # 6. Remove rows containing non-finite feature values
    # -----------------------------------------------------

    rows_with_nonfinite = df.isna().any(axis=1)
    removed_nonfinite = int(rows_with_nonfinite.sum())

    df = df.loc[~rows_with_nonfinite].copy()

    total_removed_nonfinite += removed_nonfinite


    # -----------------------------------------------------
    # 7. Add binary attack target
    # -----------------------------------------------------

    df["attack_binary"] = (df["Label"] != "BENIGN").astype(int)


    # -----------------------------------------------------
    # 8. Preserve temporal/source information
    # -----------------------------------------------------

    df["source_file"] = file_path.name


    # -----------------------------------------------------
    # 9. Save processed file
    # -----------------------------------------------------

    output_path = processed_folder / file_path.name

    df.to_csv(output_path, index=False)

    rows_after = len(df)
    total_after += rows_after

    print(f"Rows before: {rows_before:,}")
    print(f"Rows removed for NaN/infinity: {removed_nonfinite:,}")
    print(f"Rows after: {rows_after:,}")

    print("Binary target distribution:")
    print(df["attack_binary"].value_counts().sort_index())

    print("Saved:", output_path)


# ---------------------------------------------------------
# 10. Final preprocessing summary
# ---------------------------------------------------------

print("\n" + "=" * 90)
print("PREPROCESSING SUMMARY")
print("=" * 90)

print(f"Rows before preprocessing: {total_before:,}")
print(f"Rows removed for non-finite values: {total_removed_nonfinite:,}")
print(f"Rows after preprocessing: {total_after:,}")

percentage_removed = (total_removed_nonfinite / total_before) * 100

print(f"Percentage removed: {percentage_removed:.4f}%")
print("\nPreprocessing complete.")