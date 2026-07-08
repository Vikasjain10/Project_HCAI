import json
from typing import Any

STRESS_FEATURE_LABELS = {
    "sleep_duration_h": "Sleep Duration",
    "activity_level": "Activity Level",
    "stress_history": "Stress History",
    "avg_hr": "Heart Rate",
}

ACTIVITY_LABELS = {0: "Sedentary", 1: "Moderate", 2: "Active"}


def _parse_explanation(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


STRESS_SCORE_MAP = {"Low": 1, "Moderate": 2, "High": 3}


def _stress_label_from_score(score: float) -> str:
    if score < 1.5:
        return "Low"
    if score < 2.5:
        return "Moderate"
    return "High"


def _compute_aggregates(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    stress_scores: list[float] = []
    wellness_scores: list[float] = []

    for session in sessions:
        label = str(session.get("stress_prediction", "")).strip()
        if label in STRESS_SCORE_MAP:
            stress_scores.append(float(STRESS_SCORE_MAP[label]))
        wellness = session.get("wellness_score")
        if wellness is not None:
            wellness_scores.append(float(wellness))

    avg_stress = round(sum(stress_scores) / len(stress_scores), 2) if stress_scores else None
    avg_wellness = round(sum(wellness_scores) / len(wellness_scores), 1) if wellness_scores else None

    return {
        "session_count": len(sessions),
        "average_stress_score": avg_stress,
        "average_stress_label": _stress_label_from_score(avg_stress) if avg_stress is not None else None,
        "average_wellness_score": avg_wellness,
    }


def _build_chart_data(sessions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chronological = sorted(sessions, key=lambda s: s["created_at"])
    chart: list[dict[str, Any]] = []
    for session in chronological:
        label = str(session.get("stress_prediction", "")).strip()
        stress_score = STRESS_SCORE_MAP.get(label)
        wellness = session.get("wellness_score")
        chart.append(
            {
                "date": session["created_at"][:10],
                "label": session["created_at"][5:10],
                "stress_label": label or "—",
                "stress_score": stress_score,
                "wellness_score": round(float(wellness), 1) if wellness is not None else None,
            }
        )
    return chart


def build_session_comparison(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    if not sessions:
        return {
            "has_data": False,
            "message": "No assessment sessions yet. Run your first assessment on Overview.",
            "sessions": [],
            "comparison": None,
        }

    ordered = sorted(sessions, key=lambda s: s["created_at"], reverse=True)
    current = ordered[0]
    previous = ordered[1] if len(ordered) > 1 else None

    comparison = None
    if previous:
        comparison = _compare_sessions(previous, current, ordered)

    tracked = ordered[:14]
    aggregates = _compute_aggregates(tracked)

    return {
        "has_data": True,
        "sessions": [_format_session(s) for s in tracked],
        "latest": _format_session(current),
        "comparison": comparison,
        "aggregates": aggregates,
        "chart_data": _build_chart_data(tracked),
        "session_count": len(sessions),
    }


def _format_session(session: dict[str, Any]) -> dict[str, Any]:
    explanation = _parse_explanation(session.get("explanation_json"))
    return {
        "id": session["id"],
        "created_at": session["created_at"],
        "inputs": {
            "avg_hr": session.get("avg_hr"),
            "rhr": session.get("rhr"),
            "sleep_duration_h": session.get("sleep_duration_h"),
            "deep_sleep_in_minutes": session.get("deep_sleep_in_minutes"),
            "steps": session.get("steps"),
            "exercise_duration": session.get("exercise_duration"),
            "stress_input": session.get("stress_input"),
            "readiness": session.get("readiness"),
            "activity_level": session.get("activity_level"),
        },
        "outputs": {
            "stress": session.get("stress_prediction"),
            "fatigue": session.get("fatigue"),
            "fatigue_type": session.get("fatigue_type"),
            "wellness_score": session.get("wellness_score"),
            "risk_score": session.get("risk_score"),
        },
        "explanation": explanation,
    }


def _compare_sessions(
    previous: dict[str, Any],
    current: dict[str, Any],
    all_sessions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    prev_stress = str(previous.get("stress_prediction", ""))
    curr_stress = str(current.get("stress_prediction", ""))
    stress_changed = prev_stress != curr_stress

    feature_changes = []
    track_fields = [
        ("sleep_duration_h", "Sleep duration", "hours", True),
        ("stress_input", "Self-reported stress", "score", True),
        ("avg_hr", "Heart rate", "bpm", True),
        ("steps", "Daily steps", "steps", False),
    ]

    for field, label, unit, lower_is_better_for_stress in track_fields:
        prev_val = previous.get(field)
        curr_val = current.get(field)
        if prev_val is None or curr_val is None:
            continue
        delta = round(float(curr_val) - float(prev_val), 2)
        if abs(delta) < 0.01:
            continue
        direction = "increased" if delta > 0 else "decreased"
        if lower_is_better_for_stress:
            stress_impact = "may increase stress" if delta > 0 else "may reduce stress"
        else:
            stress_impact = "may reduce stress" if delta > 0 else "may increase stress"
        feature_changes.append(
            {
                "feature": field,
                "label": label,
                "previous": prev_val,
                "current": curr_val,
                "delta": delta,
                "direction": direction,
                "stress_impact": stress_impact,
                "message": f"{label} {direction} ({abs(delta)} {unit}) — {stress_impact}",
            }
        )

    prev_activity = previous.get("activity_level")
    curr_activity = current.get("activity_level")
    if prev_activity and curr_activity and prev_activity != curr_activity:
        feature_changes.append(
            {
                "feature": "activity_level",
                "label": "Activity level",
                "previous": prev_activity,
                "current": curr_activity,
                "delta": None,
                "direction": "changed",
                "stress_impact": "may affect stress",
                "message": f"Activity level changed from {prev_activity} to {curr_activity}",
            }
        )

    summary_parts = []
    if stress_changed:
        summary_parts.append(f"Stress level changed from {prev_stress} to {curr_stress}")
    elif feature_changes:
        summary_parts.append(f"Stress level remains {curr_stress}")
    else:
        summary_parts.append("Metrics are similar to your previous session")

    if feature_changes:
        summary_parts.append(feature_changes[0]["message"])

    aggregates = _compute_aggregates(all_sessions) if all_sessions else None

    return {
        "previous_session_id": previous["id"],
        "current_session_id": current["id"],
        "stress_changed": stress_changed,
        "previous_stress": prev_stress,
        "current_stress": curr_stress,
        "feature_changes": feature_changes[:5],
        "summary": ". ".join(summary_parts) + ".",
        "aggregates": aggregates,
    }
