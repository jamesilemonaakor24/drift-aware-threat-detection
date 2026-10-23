
from pathlib import Path
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix

# =====================================
# 1. FIND OUR PROJECT FILES
# =====================================

project = Path(__file__).resolve().parents[1]
folder = project / "data" / "processed"

splits = pd.read_csv(
    folder / "experiment_splits.csv"
)

saved = joblib.load(
    project / "experiments" / "artifacts"
    / "baseline_random_forest.joblib"
)

original_model = saved["model"]
original_features = saved["features"]

# Remove Destination Port from the new model
new_features = [
    feature for feature in original_features
    if feature != "Destination Port"
]

assert len(new_features) == len(original_features) - 1

# =====================================
# 2. LOAD TRAINING AND TEST DATA
# =====================================

training_parts = []
test_parts = []

for day in ["Monday", "Tuesday"]:

    file = next(folder.glob(f"{day}*.csv"))
    df = pd.read_csv(file)

    for split_name, destination in [
        ("training", training_parts),
        ("known_test", test_parts)
    ]:

        rows = splits.loc[
            (splits["source_file"] == file.name)
            & (splits["split"] == split_name),
            "row_number"
        ].to_numpy()

        destination.append(df.iloc[rows].copy())

train = pd.concat(training_parts, ignore_index=True)
test = pd.concat(test_parts, ignore_index=True)

X_train = train[new_features].astype("float32")
y_train = train["attack_binary"]

X_test = test[new_features].astype("float32")
y_test = test["attack_binary"]

# =====================================
# 3. TRAIN WITHOUT DESTINATION PORT
# =====================================

new_model = RandomForestClassifier(
    n_estimators=80,
    max_depth=18,
    min_samples_leaf=5,
    class_weight="balanced_subsample",
    random_state=42,
    n_jobs=-1
)

print("Training without Destination Port...")

new_model.fit(X_train, y_train)

# =====================================
# 4. COMPARE BOTH SECURITY GUARDS
# =====================================

original_predictions = original_model.predict(
    test[original_features].astype("float32")
)

new_predictions = new_model.predict(X_test)

def show_results(name, predictions):

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1]
    ).ravel()

    recall = tp / (tp + fn) if (tp + fn) else 0
    fpr = fp / (fp + tn) if (fp + tn) else 0

    print(f"\n--- {name} ---")
    print(f"Attacks detected: {tp:,}")
    print(f"Missed attacks: {fn:,}")
    print(f"False alarms: {fp:,}")
    print(f"Attack recall: {recall:.2%}")
    print(f"False Positive Rate: {fpr:.4%}")

    for attack in ["FTP - Patator", "SSH - Patator"]:
        mask = test["Label"] == attack
        total = int(mask.sum())
        detected = int((predictions[mask] == 1).sum())

        print(
            f"{attack}: {detected:,}/{total:,} detected"
        )

show_results(
    "ORIGINAL MODEL (WITH PORT)",
    original_predictions
)

show_results(
    "NEW MODEL (WITHOUT PORT)",
    new_predictions
)

print("\nWednesday data was NOT used.")
print("The original saved model was NOT changed.")
