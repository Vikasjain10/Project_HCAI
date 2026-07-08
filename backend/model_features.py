"""Shared stress-model feature definitions and helpers."""

STRESS_FEATURES = [
    "sleep_duration_h",
    "activity_level",
    "stress_history",
    "avg_hr",
]

STRESS_MODEL_FEATURES = [
    "avg_hr",
    "rhr",
    "deep_sleep_in_minutes",
    "minutes_asleep",
    "steps",
    "exercise_duration",
    "overall_score",
    "restlessness",
]

FATIGUE_FEATURES = [
    "avg_hr",
    "rhr",
    "sleep_duration_h",
    "deep_sleep_in_minutes",
    "steps",
    "exercise_duration",
    "stress",
    "readiness",
]

STRESS_FEATURE_LABELS = {
    "sleep_duration_h": "Sleep Duration",
    "activity_level": "Activity Level",
    "stress_history": "Physiological Load (history)",
    "avg_hr": "Heart Rate",
}

STRESS_MODEL_LABELS = {
    "avg_hr": "Average Heart Rate",
    "rhr": "Resting Heart Rate",
    "deep_sleep_in_minutes": "Deep Sleep",
    "minutes_asleep": "Sleep Duration",
    "steps": "Daily Steps",
    "exercise_duration": "Exercise Duration",
    "overall_score": "Sleep Quality Score",
    "restlessness": "Restlessness",
}

FATIGUE_FEATURE_LABELS = {
    "avg_hr": "Average Heart Rate",
    "rhr": "Resting Heart Rate",
    "sleep_duration_h": "Sleep Duration",
    "deep_sleep_in_minutes": "Deep Sleep",
    "steps": "Daily Steps",
    "exercise_duration": "Exercise Duration",
    "stress": "Self-reported Stress",
    "readiness": "Readiness",
}

ACTIVITY_MAP = {"sedentary": 0, "moderate": 1, "active": 2}
ACTIVITY_LABELS = {0: "Sedentary", 1: "Moderate", 2: "Active"}


def steps_to_activity_level(steps: float) -> int:
    if steps < 5000:
        return 0
    if steps < 10000:
        return 1
    return 2


def profile_to_activity_level(activity_level: str | None, steps: float | None = None) -> int:
    if steps is not None:
        return steps_to_activity_level(float(steps))
    if activity_level:
        return ACTIVITY_MAP.get(activity_level.lower(), 1)
    return 1


def compute_physiological_load(
    *,
    avg_hr: float,
    rhr: float,
    sleep_duration_h: float,
    steps: float,
    deep_sleep_in_minutes: float = 90.0,
) -> float:
    """Objective 0-100 load score from wearable metrics only (no self-report)."""
    hr_load = min(100.0, max(0.0, (float(avg_hr) - 55.0) / 45.0 * 100.0))
    rhr_load = min(100.0, max(0.0, (float(rhr) - 50.0) / 30.0 * 100.0))
    sleep_def = min(100.0, max(0.0, (8.0 - float(sleep_duration_h)) / 4.0 * 100.0))
    activity_def = min(100.0, max(0.0, (8000.0 - float(steps)) / 8000.0 * 100.0))
    deep_def = min(100.0, max(0.0, (90.0 - float(deep_sleep_in_minutes)) / 60.0 * 100.0))
    return round(
        hr_load * 0.30 + rhr_load * 0.15 + sleep_def * 0.25 + activity_def * 0.20 + deep_def * 0.10,
        1,
    )


def build_stress_features(
    *,
    sleep_duration_h: float,
    avg_hr: float,
    rhr: float,
    steps: float,
    deep_sleep_in_minutes: float,
    activity_level: str | None = None,
    prior_physiological_load: float | None = None,
) -> dict[str, float]:
    current_load = compute_physiological_load(
        avg_hr=avg_hr,
        rhr=rhr,
        sleep_duration_h=sleep_duration_h,
        steps=steps,
        deep_sleep_in_minutes=deep_sleep_in_minutes,
    )
    if prior_physiological_load is None:
        history = current_load
    else:
        history = round(0.5 * current_load + 0.5 * float(prior_physiological_load), 1)
    return {
        "sleep_duration_h": float(sleep_duration_h),
        "activity_level": float(profile_to_activity_level(activity_level, steps)),
        "stress_history": history,
        "avg_hr": float(avg_hr),
    }


def build_stress_model_features(data: dict) -> dict[str, float]:
    sleep_duration_h = float(data["sleep_duration_h"])
    deep_sleep = float(data["deep_sleep_in_minutes"])
    return {
        "avg_hr": float(data["avg_hr"]),
        "rhr": float(data["rhr"]),
        "deep_sleep_in_minutes": deep_sleep,
        "minutes_asleep": sleep_duration_h * 60,
        "steps": float(data["steps"]),
        "exercise_duration": float(data["exercise_duration"]),
        "overall_score": ((sleep_duration_h / 8) * 50) + ((deep_sleep / 120) * 50),
        "restlessness": max(0, 1 - (deep_sleep / 120)),
    }


def build_fatigue_features(data: dict) -> dict[str, float]:
    return {key: float(data[key]) for key in FATIGUE_FEATURES}
