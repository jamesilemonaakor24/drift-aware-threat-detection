import pandas as pd
import numpy as np
from pathlib import Path

# ---------------------------------------------------------
# 1. Locate the raw CIC-IDS2017 CSV files
# ---------------------------------------------------------

data_folder = Path("data/raw/MachineLearningCVE")
csv_files = sorted(data_folder.glob("*.csv"))

print(f"CSV files found: {len(csv_files)}")

if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {data_folder}")


# ---------------------------------------------------------
# 2. Variables used to build an overall dataset summary
# ---------------------------------------------------------

total_rows = 0
reference_columns = None
overall_labels = pd.Series(dtype="int64")
audit_summary = []


# ---------------------------------------------------------
# 3. Audit every CSV file separately
# ---------------------------------------------------------

for file_path in csv_files:

    print("\n" + "=" * 90)
    print("FILE:", file_path.name)
    print("=" * 90)

    df = pd.read_csv(file_path)

    rows, columns = df.shape
    total_rows += rows

    print(f"Shape: {rows:,} rows x {columns} columns")


    # -----------------------------------------------------
    # Schema consistency
    # -----------------------------------------------------

    if reference_columns is None:
        reference_columns = df.columns.tolist()
        columns_match = True
    else:
        columns_match = df.columns.tolist() == reference_columns

    print("Columns match reference:", columns_match)


    # -----------------------------------------------------
    # Label distribution
    # -----------------------------------------------------

    label_column = " Label"

    label_counts = df[label_column].value_counts(dropna=False)

    print("\nLabel distribution:")
    print(label_counts)

    overall_labels = overall_labels.add(label_counts, fill_value=0)


    # -----------------------------------------------------
    # Missing values
    # -----------------------------------------------------

    missing_by_column = df.isnull().sum()
    missing_by_column = missing_by_column[missing_by_column > 0]

    total_missing = int(missing_by_column.sum())

    print("\nMissing values:", total_missing)

    if total_missing > 0:
        print("Columns containing missing values:")
        print(missing_by_column)
    else:
        print("No missing values found.")


    # -----------------------------------------------------
    # Infinite numerical values
    # -----------------------------------------------------

    numeric_df = df.select_dtypes(include=[np.number])

    infinite_by_column = np.isinf(numeric_df).sum()
    infinite_by_column = infinite_by_column[infinite_by_column > 0]

    total_infinite = int(infinite_by_column.sum())

    print("\nInfinite values:", total_infinite)

    if total_infinite > 0:
        print("Columns containing infinite values:")
        print(infinite_by_column)
    else:
        print("No infinite values found.")


    # -----------------------------------------------------
    # Duplicate rows
    # -----------------------------------------------------

    duplicate_rows = int(df.duplicated().sum())

    print("\nDuplicate rows:", duplicate_rows)

    duplicate_data = df[df.duplicated(keep=False)]

    if not duplicate_data.empty:
        print("Rows belonging to duplicated groups by label:")
        print(duplicate_data[label_column].value_counts())
    else:
        print("No duplicated rows found.")


    # -----------------------------------------------------
    # Constant / zero-variance columns
    # -----------------------------------------------------

    unique_counts = df.nunique(dropna=False)

    constant_columns = unique_counts[unique_counts <= 1].index.tolist()

    print("\nConstant columns:", len(constant_columns))

    if constant_columns:
        for column in constant_columns:
            print(" -", repr(column))


    # -----------------------------------------------------
    # Data types
    # -----------------------------------------------------

    dtype_counts = df.dtypes.astype(str).value_counts()

    print("\nData type summary:")
    print(dtype_counts)


    # -----------------------------------------------------
    # Label formatting / encoding inspection
    # -----------------------------------------------------

    suspicious_labels = [
        label
        for label in df[label_column].dropna().unique()
        if "\ufffd" in str(label)
    ]

    print("\nLabels containing replacement/encoding character:")

    if suspicious_labels:
        for label in suspicious_labels:
            print(" -", repr(label))
    else:
        print("None")


    # -----------------------------------------------------
    # Store file-level results for final summary
    # -----------------------------------------------------

    audit_summary.append(
        {
            "file": file_path.name,
            "rows": rows,
            "columns": columns,
            "schema_match": columns_match,
            "missing_values": total_missing,
            "infinite_values": total_infinite,
            "duplicate_rows": duplicate_rows,
            "constant_columns": len(constant_columns),
        }
    )


# ---------------------------------------------------------
# 4. Overall dataset summary
# ---------------------------------------------------------

summary_df = pd.DataFrame(audit_summary)

print("\n\n" + "=" * 90)
print("OVERALL CIC-IDS2017 AUDIT SUMMARY")
print("=" * 90)

print("\nFiles analysed:", len(csv_files))
print(f"Total network flows: {total_rows:,}")
print("Number of columns:", len(reference_columns))

print("\nFile-level summary:")
print(summary_df.to_string(index=False))


# ---------------------------------------------------------
# 5. Overall class distribution
# ---------------------------------------------------------

overall_labels = overall_labels.sort_values(ascending=False).astype(int)

print("\nOverall label distribution:")
print(overall_labels)

print("\nTotal labelled flows:", int(overall_labels.sum()))


# ---------------------------------------------------------
# 6. Final schema check
# ---------------------------------------------------------

if summary_df["schema_match"].all():
    print("\nSchema check: PASS - all CSV files use the same columns and order.")
else:
    print("\nSchema check: FAIL - at least one CSV has a different schema.")


# ---------------------------------------------------------
# 7. Overall data-quality totals
# ---------------------------------------------------------

print(
    "\nTotal missing values:",
    int(summary_df["missing_values"].sum())
)

print(
    "Total infinite values:",
    int(summary_df["infinite_values"].sum())
)

print(
    "Total within-file duplicate rows:",
    int(summary_df["duplicate_rows"].sum())
)

print("\nAudit complete.")