import pandas as pd

df = pd.read_csv("data/final_dataset.csv")

def fatigue_type(row):
    if row["sleep_quality"] <= 2 and row["sleep_duration_h"] < 6:
        return "Sleep"
    elif row["soreness"] >= 4:
        return "Physical"
    elif row["stress"] >= 4:
        return "Stress"
    else:
        return "General"

df["fatigue_type"] = df.apply(fatigue_type, axis=1)

df.to_csv("data/final_dataset.csv", index=False)

print("--- FATIGUE TYPE DISTRIBUTION ---")
print(df["fatigue_type"].value_counts())