import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------
df = pd.read_csv("data/final_dataset.csv")

# ---------------------------------------------------------
# CLEAN FEATURES (MATCH API)
# ---------------------------------------------------------
features = [
    "avg_hr",
    "rhr",
    "sleep_duration_h",
    "deep_sleep_in_minutes",
    "steps",
    "exercise_duration",
    "stress",
    "readiness"
]

X = df[features].fillna(df[features].median())

# Target
y = df["fatigue_label"]

# ---------------------------------------------------------
# Handle imbalance
# ---------------------------------------------------------
neg_count = (y == 0).sum()
pos_count = (y == 1).sum()
ratio = neg_count / pos_count if pos_count != 0 else 1

# ---------------------------------------------------------
# Train/Test Split
# ---------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# ---------------------------------------------------------
# Model
# ---------------------------------------------------------
model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    scale_pos_weight=ratio,
    random_state=42,
    eval_metric="logloss"
)

model.fit(X_train, y_train)

# ---------------------------------------------------------
# Evaluation
# ---------------------------------------------------------
print("\nClassification Report:\n")
print(classification_report(y_test, model.predict(X_test)))

# ---------------------------------------------------------
# Save Model
# ---------------------------------------------------------
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/fatigue_model.pkl")

print("\nModel saved successfully ✔")