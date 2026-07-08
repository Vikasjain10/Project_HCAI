import pandas as pd

from wellness_engine import (
    calculate_heart_score,
    calculate_sleep_score,
    calculate_activity_score,
    calculate_stress_score,
    calculate_recovery_score,
    calculate_wellness_score,
    wellness_category
)

print("Loading dataset...")

df = pd.read_csv("data/final_dataset.csv")

print("Calculating wellness components...")

# ---------------------------------------------------------
# HEART SCORE
# ---------------------------------------------------------
df["heart_score"] = df.apply(
    lambda row: calculate_heart_score(
        row["avg_hr"],
        row["rhr"]
    ),
    axis=1
)

# ---------------------------------------------------------
# SLEEP SCORE
# ---------------------------------------------------------
df["sleep_score_component"] = df.apply(
    lambda row: calculate_sleep_score(
        row["sleep_duration_h"],
        row["deep_sleep_in_minutes"]
    ),
    axis=1
)

# ---------------------------------------------------------
# ACTIVITY SCORE
# ---------------------------------------------------------
df["activity_score_component"] = df.apply(
    lambda row: calculate_activity_score(
        row["steps"],
        row["exercise_duration"]
    ),
    axis=1
)

# ---------------------------------------------------------
# STRESS SCORE
# ---------------------------------------------------------
df["stress_score_component"] = df["stress"].apply(
    calculate_stress_score
)

# ---------------------------------------------------------
# RECOVERY SCORE
# ---------------------------------------------------------
df["recovery_score_component"] = df.apply(
    lambda row: calculate_recovery_score(
        row["readiness"],
        row["rhr"]
    ),
    axis=1
)

# ---------------------------------------------------------
# WELLNESS SCORE
# ---------------------------------------------------------
df["wellness_score"] = df.apply(
    lambda row: calculate_wellness_score(
        row["heart_score"],
        row["sleep_score_component"],
        row["activity_score_component"],
        row["stress_score_component"],
        row["recovery_score_component"]
    ),
    axis=1
)

# ---------------------------------------------------------
# CATEGORY
# ---------------------------------------------------------
df["wellness_category"] = df["wellness_score"].apply(
    wellness_category
)

# Save
df.to_csv(
    "data/final_dataset.csv",
    index=False
)

print("\nWellness calculation completed successfully!\n")

print(df[[
    "heart_score",
    "sleep_score_component",
    "activity_score_component",
    "stress_score_component",
    "recovery_score_component",
    "wellness_score",
    "wellness_category"
]].head())