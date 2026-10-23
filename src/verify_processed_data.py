import pandas as pd
import numpy as np
from pathlib import Path


# Where our cleaned files are stored
processed_folder = Path("data/processed")

csv_files = sorted(processed_folder.glob("*.csv"))

print(f"Processed files found: {len(csv_files)}")

if not csv_files:
    raise FileNotFoundError("No processed CSV files were found.")


total_rows = 0
all_checks_passed = True


for file_path in csv_files:

    print("\n" + "=" * 80)
    print("Checking:", file_path.name)

    df = pd.read_csv(file_path)

    total_rows += len(df)


    # 1. Check for missing values
    missing_values = int(df.isna().sum().sum())

    print("Missing values:", missing_values)

    if missing_values != 0:
        all_checks_passed = False


    # 2. Check for infinity
    numeric_df = df.select_dtypes(include=[np.number])

    infinite_values = int(np.isinf(numeric_df).sum().sum())

    print("Infinite values:", infinite_values)

    if infinite_values != 0:
        all_checks_passed = False


    # 3. Check that column names have no extra spaces
    bad_column_names = [
        column
        for column in df.columns
        if column != column.strip()
    ]

    print("Column names with extra spaces:", len(bad_column_names))

    if bad_column_names:
        all_checks_passed = False


    # 4. Check that our binary target exists
    binary_exists = "attack_binary" in df.columns

    print("attack_binary exists:", binary_exists)

    if not binary_exists:
        all_checks_passed = False


    # 5. Check binary target contains only 0 and 1
    if binary_exists:

        binary_values = sorted(df["attack_binary"].unique())

        print("attack_binary values:", binary_values)

        if not set(binary_values).issubset({0, 1}):
            all_checks_passed = False


    # 6. Check that source_file exists
    source_exists = "source_file" in df.columns

    print("source_file exists:", source_exists)

    if not source_exists:
        all_checks_passed = False


    # 7. Check for broken label characters
    broken_labels = df[
        df["Label"].astype(str).str.contains("�", regex=False)
    ]

    print("Rows with broken label character:", len(broken_labels))

    if len(broken_labels) != 0:
        all_checks_passed = False


    # 8. Check that binary labels agree with Label
    expected_binary = (df["Label"] != "BENIGN").astype(int)

    incorrect_binary = int(
        (df["attack_binary"] != expected_binary).sum()
    )

    print("Incorrect binary labels:", incorrect_binary)

    if incorrect_binary != 0:
        all_checks_passed = False


print("\n" + "=" * 80)
print("FINAL VERIFICATION")
print("=" * 80)

print(f"Files checked: {len(csv_files)}")
print(f"Total processed rows: {total_rows:,}")

if all_checks_passed:
    print("RESULT: PASS")
    print("Processed data passed all checks.")
else:
    print("RESULT: FAIL")
    print("One or more problems were found.")