import os
import pandas as pd
import json

# --- Your Processing Functions ---
def load_rhr(filepath):
    df = pd.read_json(filepath)
    df["date"] = pd.to_datetime(df["dateTime"]).dt.date
    df["rhr"] = df["value"].apply(lambda x: x.get("value") if isinstance(x, dict) else None)
    return df[["date", "rhr"]].dropna()

def load_heart_rate(filepath):
    df = pd.read_json(filepath)
    df["date"] = pd.to_datetime(df["dateTime"]).dt.date
    df["bpm"] = df["value"].apply(lambda x: x.get("bpm") if isinstance(x, dict) else None)
    daily_hr = df.groupby("date")["bpm"].mean().reset_index()
    daily_hr.rename(columns={"bpm": "avg_hr"}, inplace=True)
    return daily_hr

def load_sleep_score(filepath):
    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    return df[["date", "overall_score", "deep_sleep_in_minutes", "resting_heart_rate", "restlessness"]]

def load_sleep(filepath):
    df = pd.read_json(filepath)
    df["date"] = pd.to_datetime(df["dateOfSleep"]).dt.date
    df.rename(columns={"minutesAsleep": "minutes_asleep", "minutesAwake": "minutes_awake", "timeInBed": "time_in_bed"}, inplace=True)
    return df[["date", "efficiency", "minutes_asleep", "minutes_awake", "time_in_bed"]]

def load_steps(filepath):
    df = pd.read_json(filepath)
    df["date"] = pd.to_datetime(df["dateTime"]).dt.date
    df["steps"] = df["value"].astype(int)
    return df.groupby("date")["steps"].sum().reset_index()

def load_exercise(filepath):
    df = pd.read_json(filepath)
    if df.empty:
        return pd.DataFrame(columns=["date", "exercise_steps", "exercise_calories", "exercise_duration"])
    df["date"] = pd.to_datetime(df["startTime"]).dt.date
    df["exercise_duration"] = df["duration"] / 60000
    df.rename(columns={"steps": "exercise_steps", "calories": "exercise_calories"}, inplace=True)
    return df.groupby("date")[["exercise_steps", "exercise_calories", "exercise_duration"]].sum().reset_index()


def process_participant(participant):
    raw_dir = f"data/raw/{participant}"
    
    wellness = pd.read_csv(f"{raw_dir}/wellness.csv")
    wellness["date"] = pd.to_datetime(wellness["effective_time_frame"]).dt.date
    
    rhr = load_rhr(f"{raw_dir}/resting_heart_rate.json")
    avg_hr = load_heart_rate(f"{raw_dir}/heart_rate.json")
    sleep_score = load_sleep_score(f"{raw_dir}/sleep_score.csv")
    sleep = load_sleep(f"{raw_dir}/sleep.json")
    steps = load_steps(f"{raw_dir}/steps.json")
    exercise = load_exercise(f"{raw_dir}/exercise.json")

    master = wellness
    master = master.merge(rhr, on="date", how="left")
    master = master.merge(avg_hr, on="date", how="left")
    master = master.merge(sleep_score, on="date", how="left")
    master = master.merge(sleep, on="date", how="left")
    master = master.merge(steps, on="date", how="left")
    master = master.merge(exercise, on="date", how="left")
    
    # STEP 1 — Add Participant ID
    master["participant_id"] = participant
    return master


# STEP 2 — Create Master Loader
participants = sorted(
    [p for p in os.listdir("data/raw") if p.startswith("p")]
)
print("Found Folders:", participants)

# STEP 3 — Process Everyone
all_data = []

for participant in participants:
    print(f"Processing {participant}...")
    try:
        master = process_participant(participant)
        all_data.append(master)
    except Exception as e:
        print(f"Skipping {participant} due to error: {e}")

final_df = pd.concat(
    all_data,
    ignore_index=True
)

# STEP 7 — Decide Targets
def stress_class(x):
    if pd.isna(x): return None
    if x <= 2:
        return "Low"
    elif x == 3:
        return "Moderate"
    else:
        return "High"

final_df["stress_label"] = (
    final_df["stress"]
    .apply(stress_class)
)

def fatigue_class(x):
    if pd.isna(x): return None
    if x <= 2:
        return 0
    else:
        return 1

final_df["fatigue_label"] = (
    final_df["fatigue"]
    .apply(fatigue_class)
)

# STEP 4 — Save Dataset
final_df.to_csv(
    "data/final_dataset.csv",
    index=False
)

# STEP 5 — Verify Size
print("\n--- MASTER LOADING COMPLETE ---")
print("Final Dataset Shape:")
print(final_df.shape)

# STEP 6 — Check Missing Values
print("\nMissing Values Per Column:")
print(final_df.isnull().sum())
def load_distance(filepath):
    df = pd.read_json(filepath)
    df["date"] = pd.to_datetime(df["dateTime"]).dt.date
    # PMData distance is typically in centimeters, converting to meters
    df["daily_distance"] = df["value"].astype(float) / 100 
    return df.groupby("date")["daily_distance"].sum().reset_index()

def load_calories(filepath):
    df = pd.read_json(filepath)
    df["date"] = pd.to_datetime(df["dateTime"]).dt.date
    df["daily_calories"] = df["value"].astype(float)
    return df.groupby("date")["daily_calories"].sum().reset_index()