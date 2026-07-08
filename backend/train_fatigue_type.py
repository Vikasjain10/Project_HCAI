import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
import os

# ---------------------------------------------------------
# Setup
# ---------------------------------------------------------
os.makedirs("models", exist_ok=True)

# ---------------------------------------------------------
# NEW CLEAN FEATURES (MATCH API)
# ---------------------------------------------------------
FEATURES = [
    "avg_hr",
    "rhr",
    "sleep_duration_h",
    "deep_sleep_in_minutes",
    "steps",
    "exercise_duration",
    "stress",
    "readiness"
]

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------
df = pd.read_csv("data/final_dataset.csv")

# Handle missing values
X = df[FEATURES].fillna(df[FEATURES].median(numeric_only=True))

# Target
y = df["fatigue_type"]

# ---------------------------------------------------------
# Train Model
# ---------------------------------------------------------
print("Training Fatigue Type Model (CLEAN FEATURES)...")

model = RandomForestClassifier(
    n_estimators=400,
    max_depth=12,
    min_samples_split=5,
    random_state=42
)

model.fit(X, y)

# ---------------------------------------------------------
# Save Model
# ---------------------------------------------------------
joblib.dump(model, "models/fatigue_type_model.pkl")

print("Model saved successfully ✔")