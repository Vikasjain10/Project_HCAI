import pandas as pd
import json

print("========================================")
print("1. WELLNESS.CSV")
try:
    df_well = pd.read_csv("data/raw/p01/wellness.csv")
    print("Columns:", df_well.columns.tolist())
    print(df_well.head(2))
except Exception as e: print("Error:", e)

print("\n========================================")
print("2. SLEEP_SCORE.CSV")
try:
    df_sleep_score = pd.read_csv("data/raw/p01/sleep_score.csv")
    print("Columns:", df_sleep_score.columns.tolist())
    print(df_sleep_score.head(2))
except Exception as e: print("Error:", e)

print("\n========================================")
print("3. HEART_RATE.JSON")
try:
    with open("data/raw/p01/heart_rate.json") as f: data = json.load(f)
    print("Type:", type(data))
    print(data[:2])
except Exception as e: print("Error:", e)

print("\n========================================")
print("4. RESTING_HEART_RATE.JSON")
try:
    with open("data/raw/p01/resting_heart_rate.json") as f: data = json.load(f)
    print(data[:2])
except Exception as e: print("Error:", e)

print("\n========================================")
print("5. SLEEP.JSON")
try:
    with open("data/raw/p01/sleep.json") as f: data = json.load(f)
    if len(data) > 0: print("Keys found:", data[0].keys())
except Exception as e: print("Error:", e)

print("\n========================================")
print("6. STEPS.JSON")
try:
    with open("data/raw/p01/steps.json") as f: data = json.load(f)
    print(data[:2])
except Exception as e: print("Error:", e)

print("\n========================================")
print("7. EXERCISE.JSON")
try:
    with open("data/raw/p01/exercise.json") as f: data = json.load(f)
    print(data[:2])
except Exception as e: print("Error:", e)
print("========================================")