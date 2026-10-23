
from pathlib import Path
import joblib
import pandas as pd

project = Path(__file__).resolve().parents[1]

saved = joblib.load(
    project / "experiments" / "artifacts"
    / "baseline_random_forest.joblib"
)

model = saved["model"]
features = saved["features"]

importance = pd.DataFrame({
    "Feature": features,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    "Importance",
    ascending=False
)

print("\n--- TOP 15 FEATURES ---")
print(importance.head(15).to_string(index=False))

print("\nTotal features:", len(features))
