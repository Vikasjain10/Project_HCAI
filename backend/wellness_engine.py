import numpy as np
import pandas as pd

# ---------------------------------------------------------
# HEART SCORE
# ---------------------------------------------------------
def calculate_heart_score(avg_hr, rhr):

    if pd.isna(avg_hr) or pd.isna(rhr):
        return 0

    # ----------------------------
    # Average Heart Rate Score
    # ----------------------------
# ------------------------------------------------
# Average Heart Rate Score
# Healthy Range = 65 to 75 bpm
# ------------------------------------------------

    if 65 <= avg_hr <= 75:
        hr_score = 100

    elif avg_hr < 65:
        difference = 65 - avg_hr
        hr_score = max(20, 100 - (difference * 3))

    else:
        difference = avg_hr - 75
        hr_score = max(20, 100 - (difference * 3))

   

    # ----------------------------
    # Resting Heart Rate Score
    # ----------------------------
    # ------------------------------------------------
# Resting Heart Rate Score
# Healthy Range = 50 to 60 bpm
# ------------------------------------------------

    if 50 <= rhr <= 60:
        rhr_score = 100

    elif rhr < 50:
        difference = 50 - rhr
        rhr_score = max(20, 100 - (difference * 4))

    else:
        difference = rhr - 60
        rhr_score = max(20, 100 - (difference * 4))

    # RHR contributes more
    heart_score = (
        0.40 * hr_score +
        0.60 * rhr_score
    )

    return round(heart_score,2)


# ---------------------------------------------------------
# SLEEP SCORE
# ---------------------------------------------------------
def calculate_sleep_score(sleep_duration, deep_sleep):

    if pd.isna(sleep_duration) or pd.isna(deep_sleep):
        return 0

    duration_score = min((sleep_duration / 8) * 100,100)
    deep_sleep_score = min((deep_sleep / 90) * 100,100)

    score = (
        0.60 * duration_score +
        0.40 * deep_sleep_score
    )

    return round(score,2)


# ---------------------------------------------------------
# ACTIVITY SCORE
# ---------------------------------------------------------
def calculate_activity_score(steps, exercise_duration):

    if pd.isna(steps):
        steps = 0

    if pd.isna(exercise_duration):
        exercise_duration = 0

    # -----------------------------
    # Steps Score
    # 10,000 steps = 100
    # -----------------------------
    steps_score = min((steps / 10000) * 100, 100)

    # -----------------------------
    # Exercise Score
    # 60 minutes = 100
    # -----------------------------
    exercise_score = min((exercise_duration / 60) * 100, 100)

    # -----------------------------
    # Final Activity Score
    # -----------------------------
    activity_score = (
        0.60 * steps_score +
        0.40 * exercise_score
    )

    return round(activity_score, 2)

# ---------------------------------------------------------
# STRESS SCORE
# ---------------------------------------------------------
def calculate_stress_score(stress):

    if pd.isna(stress):
        return 50

    # Frontend sends stress from 0-100
    score = 100 - stress

    return round(score, 2)

# ---------------------------------------------------------
# RECOVERY SCORE
# ---------------------------------------------------------
def calculate_recovery_score(readiness, rhr):

    if pd.isna(readiness):
        readiness = 5

    # Frontend already sends readiness between 0 and 100
    readiness_score = readiness

    if pd.isna(rhr):
        rhr_component = 50

    elif rhr <=55:
        rhr_component =100

    elif rhr <=60:
        rhr_component =90

    elif rhr <=70:
        rhr_component =75

    elif rhr <=80:
        rhr_component =55

    else:
        rhr_component =35

    recovery = (
        0.60*readiness_score +
        0.40*rhr_component
    )

    return round(recovery,2)


# ---------------------------------------------------------
# FINAL WELLNESS SCORE
# ---------------------------------------------------------
def calculate_wellness_score(
    heart_score,
    sleep_score,
    activity_score,
    stress_score,
    recovery_score
):

    wellness = (

        0.35*heart_score +

        0.25*sleep_score +

        0.20*recovery_score +

        0.10*activity_score +

        0.10*stress_score

    )


    return round(wellness,2)


# ---------------------------------------------------------
# CATEGORY
# --------------------------------------------------------- 


def wellness_category(score):

    if score>=85:
        return "Excellent"

    elif score>=70:
        return "Good"

    elif score>=50:
        return "Moderate"

    else:
        return "Poor"