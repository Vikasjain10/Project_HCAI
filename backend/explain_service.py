import os
from typing import Any

import joblib
import numpy as np
import pandas as pd
import shap

from model_features import (
    ACTIVITY_LABELS,
    FATIGUE_FEATURES,
    FATIGUE_FEATURE_LABELS,
    STRESS_FEATURES,
    STRESS_FEATURE_LABELS,
    STRESS_MODEL_FEATURES,
    STRESS_MODEL_LABELS,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

_stress_model = joblib.load(os.path.join(MODEL_DIR, "stress_model.pkl"))
_fatigue_model = joblib.load(os.path.join(MODEL_DIR, "fatigue_model.pkl"))
_stress_explainer = shap.TreeExplainer(_stress_model)
_fatigue_explainer = shap.TreeExplainer(_fatigue_model)

STRESS_OPTIMAL = {
    "sleep_duration_h": 8.0,
    "activity_level": 2.0,
    "stress_history": 25.0,
    "avg_hr": 68.0,
}

FATIGUE_OPTIMAL = {
    "avg_hr": 68.0,
    "rhr": 60.0,
    "sleep_duration_h": 8.0,
    "deep_sleep_in_minutes": 90.0,
    "steps": 10000.0,
    "exercise_duration": 45.0,
    "stress": 30.0,
    "readiness": 75.0,
}

WELLNESS_WEIGHTS = {
    "sleep": 0.30,
    "activity": 0.25,
    "recovery": 0.25,
    "stress_control": 0.10,
    "exercise": 0.10,
}

WELLNESS_LABELS = {
    "sleep": "Sleep",
    "activity": "Activity (steps)",
    "recovery": "Recovery (readiness)",
    "stress_control": "Stress control",
    "exercise": "Exercise",
}


def _shap_for_class(explainer, model, row: pd.DataFrame, class_label) -> np.ndarray:
    shap_values = explainer.shap_values(row)
    features = list(row.columns)

    if isinstance(shap_values, list):
        classes = list(model.classes_)
        class_index = classes.index(class_label) if class_label in classes else 0
        values = np.asarray(shap_values[class_index]).reshape(-1)
    else:
        values = np.asarray(shap_values).reshape(-1)

    if len(values) != len(features):
        values = np.asarray(explainer(row.values).values).reshape(-1)[: len(features)]

    return values


def _format_stress_value(feature: str, value: float) -> str:
    if feature == "activity_level":
        return ACTIVITY_LABELS.get(int(round(value)), str(value))
    if feature == "sleep_duration_h":
        return f"{value:.1f} h"
    if feature == "stress_history":
        return f"{value:.0f}/100 load"
    return f"{value:.0f} bpm"


def _format_fatigue_value(feature: str, value: float) -> str:
    if feature == "sleep_duration_h":
        return f"{value:.1f} h"
    if feature in {"avg_hr", "rhr"}:
        return f"{value:.0f} bpm"
    if feature == "deep_sleep_in_minutes":
        return f"{value:.0f} min"
    if feature == "steps":
        return f"{value:.0f} steps"
    if feature == "exercise_duration":
        return f"{value:.0f} min"
    if feature == "stress":
        return f"{value:.0f}/100"
    if feature == "readiness":
        return f"{value:.0f}/100"
    return str(value)


def _stress_impact_message(feature: str, value: float, shap_value: float) -> str:
    label = STRESS_FEATURE_LABELS[feature]
    optimal = STRESS_OPTIMAL[feature]

    if feature == "sleep_duration_h":
        if value < optimal:
            return f"Low sleep ({value:.1f}h) increases stress score"
        return f"Healthy sleep ({value:.1f}h) reduces stress score"
    if feature == "activity_level":
        level = ACTIVITY_LABELS.get(int(round(value)), "Moderate")
        if value >= 1:
            return f"{level} activity reduces stress score"
        return f"{level} activity increases stress score"
    if feature == "stress_history":
        if value > optimal:
            return f"Elevated physiological load ({value:.0f}) increases stress score"
        return f"Lower physiological load ({value:.0f}) reduces stress score"
    if feature == "avg_hr":
        if value > optimal:
            return f"Elevated heart rate ({value:.0f} bpm) increases stress score"
        return f"Stable heart rate ({value:.0f} bpm) reduces stress score"

    direction = "increases" if shap_value > 0 else "reduces"
    return f"{label} {direction} stress score"


def _fatigue_impact_message(
    feature: str,
    value: float,
    shap_value: float,
    fatigue_label: int,
) -> str:
    label = FATIGUE_FEATURE_LABELS[feature]
    display = _format_fatigue_value(feature, value)
    direction = _fatigue_direction(shap_value, fatigue_label)
    if direction == "increases_fatigue":
        return f"{label} ({display}) pushes toward fatigue"
    return f"{label} ({display}) lowers fatigue likelihood"


def _wellness_impact_message(key: str, score: float, weight: float) -> str:
    label = WELLNESS_LABELS[key]
    contribution = round(score * weight, 1)
    max_pts = round(100 * weight, 1)

    if score >= 70:
        return f"Strong {label} ({score}/100) adds {contribution} of {max_pts} possible points"
    if score >= 40:
        return f"Moderate {label} ({score}/100) contributes {contribution} of {max_pts} possible points"
    return f"Low {label} ({score}/100) only adds {contribution} of {max_pts} possible points — main drag on wellness"


def _format_stress_model_value(feature: str, value: float) -> str:
    if feature in {"avg_hr", "rhr"}:
        return f"{value:.0f} bpm"
    if feature == "deep_sleep_in_minutes":
        return f"{value:.0f} min"
    if feature == "minutes_asleep":
        return f"{value / 60:.1f} h"
    if feature == "steps":
        return f"{value:.0f} steps"
    if feature == "exercise_duration":
        return f"{value:.0f} min"
    if feature == "overall_score":
        return f"{value:.0f}/100"
    if feature == "restlessness":
        return f"{value:.2f}"
    return str(value)


def _stress_model_impact_message(feature: str, value: float, shap_value: float) -> str:
    label = STRESS_MODEL_LABELS[feature]
    direction = "increases" if shap_value > 0 else "reduces"
    return f"{label} ({_format_stress_model_value(feature, value)}) {direction} stress score"


def explain_prediction(stress_features: dict[str, float], stress_label: str) -> dict[str, Any]:
    use_model_features = all(k in stress_features for k in STRESS_MODEL_FEATURES)
    features = STRESS_MODEL_FEATURES if use_model_features else STRESS_FEATURES
    labels = STRESS_MODEL_LABELS if use_model_features else STRESS_FEATURE_LABELS
    row = pd.DataFrame([[stress_features[f] for f in features]], columns=features)
    values = _shap_for_class(_stress_explainer, _stress_model, row, stress_label)

    feature_impacts = []
    for idx, feature in enumerate(features):
        value = float(stress_features[feature])
        shap_value = float(values[idx])
        message = (
            _stress_model_impact_message(feature, value, shap_value)
            if use_model_features
            else _stress_impact_message(feature, value, shap_value)
        )
        display_value = (
            _format_stress_model_value(feature, value)
            if use_model_features
            else _format_stress_value(feature, value)
        )
        feature_impacts.append(
            {
                "feature": feature,
                "label": labels[feature],
                "value": value,
                "display_value": display_value,
                "shap_value": round(shap_value, 4),
                "direction": "increases_stress" if shap_value > 0 else "reduces_stress",
                "message": message,
            }
        )

    feature_impacts.sort(key=lambda item: abs(item["shap_value"]), reverse=True)
    top = feature_impacts[:3]
    summary = " ".join(item["message"] + "." for item in top[:2])
    if not summary:
        summary = "Your metrics are balanced, supporting a stable stress profile."

    return {
        "summary": summary,
        "feature_impacts": feature_impacts,
        "top_drivers": [item["label"] for item in top],
        "model_type": "RandomForest + SHAP",
        "predicted_label": stress_label,
    }


def _fatigue_direction(shap_value: float, fatigue_label: int) -> str:
    """Map SHAP sign to UI direction for the predicted fatigue class."""
    if fatigue_label == 1:
        return "increases_fatigue" if shap_value > 0 else "reduces_fatigue"
    return "increases_fatigue" if shap_value < 0 else "reduces_fatigue"


def _order_fatigue_impacts(feature_impacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    risk = [item for item in feature_impacts if item["direction"] == "increases_fatigue"]
    protective = [item for item in feature_impacts if item["direction"] == "reduces_fatigue"]
    risk.sort(key=lambda item: abs(item["shap_value"]), reverse=True)
    protective.sort(key=lambda item: abs(item["shap_value"]), reverse=True)
    return risk + protective


def explain_fatigue(fatigue_features: dict[str, float], fatigue: int) -> dict[str, Any]:
    fatigue_label = 1 if int(fatigue) == 1 else 0
    row = pd.DataFrame([[fatigue_features[f] for f in FATIGUE_FEATURES]], columns=FATIGUE_FEATURES)
    values = _shap_for_class(_fatigue_explainer, _fatigue_model, row, fatigue_label)

    feature_impacts = []
    for idx, feature in enumerate(FATIGUE_FEATURES):
        value = float(fatigue_features[feature])
        shap_value = float(values[idx])
        direction = _fatigue_direction(shap_value, fatigue_label)
        feature_impacts.append(
            {
                "feature": feature,
                "label": FATIGUE_FEATURE_LABELS[feature],
                "value": value,
                "display_value": _format_fatigue_value(feature, value),
                "shap_value": round(shap_value, 4),
                "direction": direction,
                "message": _fatigue_impact_message(feature, value, shap_value, fatigue_label),
            }
        )

    feature_impacts = _order_fatigue_impacts(feature_impacts)
    top = feature_impacts[:3]
    predicted = "Yes" if fatigue_label == 1 else "No"
    summary_parts = [item["message"] + "." for item in top[:2]]
    summary = " ".join(summary_parts)
    if not summary:
        summary = (
            "Your wearable metrics are balanced, supporting a low-fatigue profile."
            if fatigue_label == 0
            else "Several wearable signals align with elevated fatigue."
        )

    return {
        "summary": summary,
        "feature_impacts": feature_impacts,
        "top_drivers": [item["label"] for item in top],
        "model_type": "RandomForest + SHAP",
        "predicted_label": predicted,
    }


def explain_wellness(breakdown: dict[str, float], score: float) -> dict[str, Any]:
    feature_impacts = []
    for key, weight in WELLNESS_WEIGHTS.items():
        component = float(breakdown.get(key, 0))
        contribution = round(component * weight, 1)
        shap_value = round((component - 50) * weight, 2)
        feature_impacts.append(
            {
                "feature": key,
                "label": WELLNESS_LABELS[key],
                "value": component,
                "display_value": f"{component}/100 ({contribution} pts)",
                "shap_value": shap_value,
                "direction": "increases_wellness" if shap_value >= 0 else "reduces_wellness",
                "message": _wellness_impact_message(key, component, weight),
                "weight_pct": int(weight * 100),
            }
        )

    feature_impacts.sort(key=lambda item: abs(item["shap_value"]), reverse=True)
    hurts = [item for item in feature_impacts if item["direction"] == "reduces_wellness"]
    helps = [item for item in feature_impacts if item["direction"] == "increases_wellness"]

    if hurts:
        summary = f"{hurts[0]['message']}. "
        if len(hurts) > 1:
            summary += f"{hurts[1]['label']} is also limiting your score."
        else:
            summary += f"Overall wellness is {score}/100."
    elif helps:
        summary = f"{helps[0]['message']}. Overall wellness is {score}/100."
    else:
        summary = f"Your wellness drivers are balanced at {score}/100."

    return {
        "summary": summary.strip(),
        "feature_impacts": feature_impacts,
        "top_drivers": [item["label"] for item in feature_impacts[:3]],
        "model_type": "Weighted wellness formula",
        "predicted_label": f"{score}/100",
    }


def build_all_explanations(
    *,
    stress_features: dict[str, float],
    fatigue_features: dict[str, float],
    stress_label: str,
    fatigue: int,
    wellness_breakdown: dict[str, float],
    wellness_score: float,
) -> dict[str, Any]:
    return {
        "stress": explain_prediction(stress_features, stress_label),
        "fatigue": explain_fatigue(fatigue_features, fatigue),
        "wellness": explain_wellness(wellness_breakdown, wellness_score),
    }
