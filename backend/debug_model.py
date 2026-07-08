import joblib
import pandas as pd

model = joblib.load("models/fatigue_model.pkl")

input_data = pd.DataFrame([{
    "avg_hr": 110.0, "rhr": 80.0, "overall_score": 20.0,
    "deep_sleep_in_minutes": 10.0, "restlessness": 0.9, "efficiency": 40.0,
    "minutes_asleep": 120.0, "minutes_awake": 200.0, "time_in_bed": 320.0,
    "steps": 500.0, "exercise_steps": 0.0, "exercise_calories": 0.0, "exercise_duration": 0.0
}])

# Get probability instead of class
prob = model.predict_proba(input_data)
print(f"Probabilities (Class 0, Class 1): {prob}")