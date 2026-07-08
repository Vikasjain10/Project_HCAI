from datetime import datetime, timedelta
from typing import Any


def _parse_date(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00").split("+")[0])
    except ValueError:
        return datetime.strptime(value[:10], "%Y-%m-%d")


def _avg(items: list[dict], key: str) -> float:
    vals = [float(i[key]) for i in items if i.get(key) is not None]
    return round(sum(vals) / len(vals), 1) if vals else 0


def build_trends(readings: list[dict[str, Any]], days: int) -> dict[str, Any]:
    if not readings:
        return {
            "has_data": False,
            "is_outdated": False,
            "message": "No data available yet",
            "series": [],
            "aggregates": {},
        }

    now = datetime.now()
    cutoff = now - timedelta(days=days)
    filtered = [r for r in readings if _parse_date(r["date"]) >= cutoff]

    if not filtered:
        latest = max(_parse_date(r["date"]) for r in readings)
        is_outdated = (now - latest).days > 30
        return {
            "has_data": False,
            "is_outdated": is_outdated,
            "message": (
                "Data is outdated or insufficient for long-term trends"
                if is_outdated
                else f"No readings in the last {days} days"
            ),
            "last_reading": latest.isoformat(),
            "series": [],
            "aggregates": {},
        }

    series = sorted(filtered, key=lambda x: x["date"])
    chart_series = [
        {
            "date": item["date"][:10],
            "avg_hr": item.get("avg_hr", 0),
            "steps": item.get("steps", 0),
            "sleep_duration_h": item.get("sleep_duration_h", 0),
            "stress": item.get("stress", 0),
            "readiness": item.get("readiness", 0),
        }
        for item in series
    ]

    aggregates = {
        "avg_hr": _avg(filtered, "avg_hr"),
        "steps": _avg(filtered, "steps"),
        "sleep_duration_h": _avg(filtered, "sleep_duration_h"),
        "stress": _avg(filtered, "stress"),
        "readiness": _avg(filtered, "readiness"),
        "count": len(filtered),
    }

    latest = max(_parse_date(r["date"]) for r in readings)
    is_outdated = (now - latest).days > 30

    return {
        "has_data": True,
        "is_outdated": is_outdated,
        "message": (
            "Data is outdated or insufficient for long-term trends"
            if is_outdated and days > 7
            else None
        ),
        "last_reading": latest.isoformat(),
        "series": chart_series,
        "aggregates": aggregates,
    }


def compute_trend_deltas(weekly: dict, monthly: dict) -> dict[str, Any]:
    w = weekly.get("aggregates", {})
    m = monthly.get("aggregates", {})
    deltas = {}
    for key in ("steps", "sleep_duration_h", "avg_hr", "stress"):
        w_val = w.get(key, 0)
        m_val = m.get(key, 0)
        if m_val:
            change = round(((w_val - m_val) / m_val) * 100, 1)
            deltas[key] = {"weekly_avg": w_val, "monthly_avg": m_val, "change_pct": change}
    return deltas