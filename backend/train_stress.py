import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
import joblib
import os

# ---------------------------------------------------------
# LOAD DATASET
# ---------------------------------------------------------
df = pd.read_csv("data/final_dataset.csv")

# Remove rows without target
df = df.dropna(subset=["stress_label"])

# ---------------------------------------------------------
# FEATURE SELECTION
# ---------------------------------------------------------
# Priority:
# 1. Heart Features
# 2. Sleep Features
# 3. Activity Features
# 4. Composite Wearable Features

features = [

    # ===============================
    # HEART FEATURES (Highest Priority)
    # ===============================
    "avg_hr",
    "rhr",

    # ===============================
    # SLEEP FEATURES (Highest Priority)
    # ===============================
    "deep_sleep_in_minutes",
    "minutes_asleep",

    # ===============================
    # ACTIVITY FEATURES (High Priority)
    # ===============================
    "steps",
    "exercise_duration",

    # ===============================
    # COMPOSITE FEATURES (Moderate)
    # ===============================
    "overall_score",
    "restlessness"

]

X = df[features].fillna(df[features].median(numeric_only=True))

y = df["stress_label"]

# ---------------------------------------------------------
# TRAIN TEST SPLIT
# ---------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# ---------------------------------------------------------
# SMOTE
# ---------------------------------------------------------
print("Applying SMOTE...")

smote = SMOTE(random_state=42)

X_train_resampled, y_train_resampled = smote.fit_resample(
    X_train,
    y_train
)

# ---------------------------------------------------------
# RANDOM FOREST MODEL
# ---------------------------------------------------------
model = RandomForestClassifier(

    n_estimators=300,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=-1

)

model.fit(
    X_train_resampled,
    y_train_resampled
)

# ---------------------------------------------------------
# PREDICTION
# ---------------------------------------------------------
predictions = model.predict(X_test)

print("\n========== STRESS MODEL REPORT ==========\n")

print(classification_report(
    y_test,
    predictions
))

# ---------------------------------------------------------
# FEATURE IMPORTANCE
# ---------------------------------------------------------
importance = pd.DataFrame({

    "Feature": features,
    "Importance": model.feature_importances_

})

importance = importance.sort_values(
    by="Importance",
    ascending=False
)

print("\n========== FEATURE IMPORTANCE ==========\n")
print(importance)

# ---------------------------------------------------------
# SAVE MODEL
# ---------------------------------------------------------
os.makedirs("models", exist_ok=True)

joblib.dump(
    model,
    "models/stress_model.pkl"
)

print("\nStress Model Saved Successfully")