import json
import pandas as pd

# =====================================================================
# Step 1: Load wellness.csv
# =====================================================================
print("Running Step 1...")
wellness = pd.read_csv("data/raw/p01/wellness.csv")
wellness["date"] = pd.to_datetime(wellness["effective_time_frame"]).dt.date


# =====================================================================
# Step 2: Process resting_heart_rate.json (Optimized for Speed)
# =====================================================================
def load_rhr(filepath):
    df = pd.read_json(filepath)
    df["date"] = pd.to_datetime(df["dateTime"]).dt.date
    # Instantly pull out the nested dictionary values without a loop
    df["rhr"] = df["value"].apply(lambda x: x.get("value") if isinstance(x, dict) else None)
    return df[["date", "rhr"]].dropna()


# =====================================================================
# Step 3: Process heart_rate.json (Optimized to prevent freezing)
# =====================================================================
def load_heart_rate(filepath):
    df = pd.read_json(filepath)
    df["date"] = pd.to_datetime(df["dateTime"]).dt.date
    # Instantly extract bpm from the millions of rows
    df["bpm"] = df["value"].apply(lambda x: x.get("bpm") if isinstance(x, dict) else None)
    
    daily_hr = df.groupby("date")["bpm"].mean().reset_index()
    daily_hr.rename(columns={"bpm": "avg_hr"}, inplace=True)
    return daily_hr


# =====================================================================
# Step 4: Process sleep_score.csv
# =====================================================================
def load_sleep_score(filepath):
    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    return df[[
        "date",
        "overall_score",
        "deep_sleep_in_minutes",
        "resting_heart_rate",
        "restlessness"
    ]]


# =====================================================================
# Step 5: Process sleep.json
# =====================================================================
def load_sleep(filepath):
    df = pd.read_json(filepath)
    df["date"] = pd.to_datetime(df["dateOfSleep"]).dt.date
    df.rename(columns={
        "minutesAsleep": "minutes_asleep",
        "minutesAwake": "minutes_awake",
        "timeInBed": "time_in_bed"
    }, inplace=True)
    return df[["date", "efficiency", "minutes_asleep", "minutes_awake", "time_in_bed"]]


# =====================================================================
# Step 6: Process steps.json
# =====================================================================
def load_steps(filepath):
    df = pd.read_json(filepath)
    df["date"] = pd.to_datetime(df["dateTime"]).dt.date
    df["steps"] = df["value"].astype(int)
    return df.groupby("date")["steps"].sum().reset_index()


# =====================================================================
# Step 7: Process exercise.json
# =====================================================================
def load_exercise(filepath):
    df = pd.read_json(filepath)
    if df.empty:
        return pd.DataFrame(columns=["date", "exercise_steps", "exercise_calories", "exercise_duration"])
    df["date"] = pd.to_datetime(df["startTime"]).dt.date
    df["exercise_duration"] = df["duration"] / 60000
    df.rename(columns={"steps": "exercise_steps", "calories": "exercise_calories"}, inplace=True)
    return df.groupby("date")[["exercise_steps", "exercise_calories", "exercise_duration"]].sum().reset_index()


# =====================================================================
# EXECUTION: Calling the functions
# =====================================================================
print("\nCalling functions to process JSON and CSV files for p01...")
print("Processing Resting Heart Rate (Step 2)...")
rhr = load_rhr("data/raw/p01/resting_heart_rate.json")

print("Processing Continuous Heart Rate (Step 3 - Should take under 5 seconds now!)...")
avg_hr = load_heart_rate("data/raw/p01/heart_rate.json")

print("Processing Sleep Scores (Step 4)...")
sleep_score = load_sleep_score("data/raw/p01/sleep_score.csv")

print("Processing Sleep Logs (Step 5)...")
sleep = load_sleep("data/raw/p01/sleep.json")

print("Processing Step Counts (Step 6)...")
steps = load_steps("data/raw/p01/steps.json")

print("Processing Exercise Data (Step 7)...")
exercise = load_exercise("data/raw/p01/exercise.json")


# =====================================================================
# Step 8: Merge Everything
# =====================================================================
print("\nStitching all data frames together into master table...")
master = wellness

master = master.merge(rhr, on="date", how="left")
master = master.merge(avg_hr, on="date", how="left")
master = master.merge(sleep_score, on="date", how="left")
master = master.merge(sleep, on="date", how="left")
master = master.merge(steps, on="date", how="left")
master = master.merge(exercise, on="date", how="left")


# =====================================================================
# Print final results to verify output
# =====================================================================
print("\n--- PHASE 4 COMPLETE FOR P01 ---")
print(f"Dataset Shape: {master.shape}")
print("\nFirst 5 rows of merged results:")
print(master.head())