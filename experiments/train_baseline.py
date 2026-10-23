
from pathlib import Path
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

# 1. Find our project and prepared data
project = Path(__file__).resolve().parents[1]
data_folder = project / "data" / "processed"

# 2. Load our saved experiment groups
splits = pd.read_csv(
    data_folder / "experiment_splits.csv"
)

training_splits = splits[
    splits["split"] == "training"
]

training_data = []

# 3. Load ONLY Monday and Tuesday training records
for day in ["Monday", "Tuesday"]:
    file = next(data_folder.glob(f"{day}*.csv"))

    row_numbers = training_splits.loc[
        training_splits["source_file"] == file.name,
        "row_number"
    ].to_numpy()

    df = pd.read_csv(file)
    selected = df.iloc[row_numbers].copy()
    training_data.append(selected)

    print(f"Loaded {day} training records: {len(selected):,}")

train = pd.concat(training_data, ignore_index=True)

# 4. Separate network features from answers
excluded = ["Label", "attack_binary", "source_file"]

X = train.drop(columns=excluded).astype("float32")
y = train["attack_binary"]

print(f"\nTotal training records: {len(X):,}")
print(f"Normal traffic: {(y == 0).sum():,}")
print(f"Attack traffic: {(y == 1).sum():,}")

# 5. Build our first machine-learning model
model = RandomForestClassifier(
    n_estimators=80,
    max_depth=18,
    min_samples_leaf=5,
    class_weight="balanced_subsample",
    random_state=42,
    n_jobs=-1
)

# 6. Train the model
print("\nTraining our original security guard...")
model.fit(X, y)

# 7. Save the trained model
output_folder = project / "experiments" / "artifacts"
output_folder.mkdir(parents=True, exist_ok=True)

model_path = output_folder / "baseline_random_forest.joblib"

joblib.dump(
    {
        "model": model,
        "features": X.columns.tolist()
    },
    model_path
)

print("\nSUCCESS: Original model trained and saved!")
print(f"Saved to: {model_path}")
print("Wednesday data was NOT used for training.")
