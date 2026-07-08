import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SYSTEM_PROMPT = """You are a health and wellness assistant for a wearable health dashboard.

Rules:
- Do NOT diagnose medical conditions
- Do NOT give medical treatment advice
- Only give lifestyle and wellness suggestions
- Keep responses practical, empathetic, and grounded in the user's numbers
- Explain WHY stress, fatigue, or wellness scores are low/high using specific metrics
- Give concrete steps the person can take to improve

When wellness score is above 85: encouraging tone, risk_level Low, is_positive true.
When wellness score is below 50: note that recovery needs attention with practical steps.

Respond ONLY with valid JSON in this exact format:
{
  "summary": "1-2 sentence overview grounded in data",
  "stress_explanation": "Why the stress level is what it is, referencing sleep, HR, activity, physiological load",
  "fatigue_explanation": "Why fatigue is or is not present, referencing sleep, steps, exercise, HR, readiness",
  "wellness_explanation": "Why the overall wellness score is at this level — which components help or hurt",
  "key_issues": ["issue with metric reference"],
  "recommendations": ["actionable tip with metric reference"],
  "risk_level": "Low | Medium | High",
  "reasoning": "How recent sessions and predictions led to these suggestions",
  "daily_suggestions": ["today tip"],
  "weekly_suggestions": ["this week tip"],
  "is_positive": false
}"""


def _build_user_prompt(
    health_data: dict[str, Any],
    predictions: dict[str, Any],
    wellness: dict[str, Any],
    sessions: dict[str, Any] | None = None,
) -> str:
    session_block = ""
    if sessions:
        comparison = sessions.get("comparison")
        latest = sessions.get("latest")
        if latest:
            session_block += f"""
Latest session ({latest.get('created_at', '')[:10]}):
- Stress prediction: {latest.get('outputs', {}).get('stress')}
- Wellness score: {latest.get('outputs', {}).get('wellness_score')}
- Sleep: {latest.get('inputs', {}).get('sleep_duration_h')}h
- Steps: {latest.get('inputs', {}).get('steps')}
"""
        if comparison:
            session_block += f"""
Session comparison:
- {comparison.get('summary', '')}
"""

    breakdown = wellness.get("breakdown") or {}
    breakdown_block = ""
    if breakdown:
        breakdown_block = "\nWellness breakdown:\n" + "\n".join(
            f"- {key}: {value}/100" for key, value in breakdown.items()
        )

    return f"""Analyze wearable data, ML predictions, and recent assessment sessions.
Explain why stress/fatigue/wellness are at their current levels and how the person can improve.

Current Wearable Data:
- Average Heart Rate: {health_data.get('avg_hr')} bpm
- Resting Heart Rate: {health_data.get('rhr')} bpm
- Sleep Duration: {health_data.get('sleep_duration_h')} hours
- Deep Sleep: {health_data.get('deep_sleep_in_minutes')} minutes
- Steps: {health_data.get('steps')}
- Exercise Duration: {health_data.get('exercise_duration')} minutes
- Self-reported Stress: {health_data.get('stress')}/100
- Readiness: {health_data.get('readiness')}/100

ML Predictions:
- Stress Level: {predictions.get('stress')}
- Fatigue: {'Yes' if predictions.get('fatigue') == 1 else 'No'}
- Fatigue Type: {predictions.get('fatigue_type')}

Wellness Score: {wellness.get('score')}/100{breakdown_block}
{session_block}"""


def _positive_recommendation(score: float, predictions: dict) -> dict[str, Any]:
    return {
        "summary": (
            f"Your overall wellness is excellent at {score}/100 — you're in a healthy range. "
            "Keep up the great work!"
        ),
        "stress_explanation": (
            f"Stress is predicted as {predictions.get('stress', 'Low')} — your wearable metrics "
            "support a balanced physiological state."
        ),
        "fatigue_explanation": (
            "No significant fatigue detected. Sleep, activity, and recovery signals look supportive."
        ),
        "wellness_explanation": (
            f"At {score}/100, your sleep, activity, and recovery components are working well together."
        ),
        "key_issues": [
            "No major concerns detected — your metrics support good overall wellness",
        ],
        "recommendations": [
            "Stay well hydrated throughout the day",
            "Maintain balanced activity with adequate rest and sleep",
            "Continue a low-stress, low-fatigue lifestyle with mindful recovery",
        ],
        "risk_level": "Low",
        "reasoning": (
            f"A wellness score of {score}/100 indicates strong balance across your tracked metrics. "
            "Focus on sustaining these habits rather than major changes."
        ),
        "daily_suggestions": [
            "Drink water regularly and take short movement breaks",
            "Keep a consistent sleep schedule tonight",
        ],
        "weekly_suggestions": [
            "Track metrics a few times this week to maintain your positive trend",
            "Schedule light activity you enjoy to stay active without overtraining",
        ],
        "is_positive": True,
    }


def _mock_recommendation(
    health_data: dict[str, Any],
    predictions: dict[str, Any],
    wellness: dict[str, Any],
    sessions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    stress = str(predictions.get("stress", "Moderate"))
    fatigue = predictions.get("fatigue", 0)
    score = float(wellness.get("score", 50))

    if score > 85:
        return _positive_recommendation(score, predictions)

    sleep = float(health_data.get("sleep_duration_h", 7))
    steps = float(health_data.get("steps", 5000))
    readiness = float(health_data.get("readiness", 50))

    key_issues = []
    recommendations = []
    daily = []
    weekly = []
    reasoning_parts = []
    stress_parts = []
    fatigue_parts = []
    wellness_parts = []

    if sleep < 7:
        key_issues.append(f"Sleep duration ({sleep}h) is below the recommended 7-8 hours")
        recommendations.append("Increase sleep duration by 1 hour with a consistent bedtime")
        daily.append("Set a bedtime alarm 30 minutes earlier tonight")
        reasoning_parts.append(f"sleep at {sleep}h is below optimal")
        stress_parts.append(f"short sleep ({sleep}h) can raise stress")
        fatigue_parts.append(f"insufficient sleep ({sleep}h) increases fatigue risk")
        wellness_parts.append(f"sleep component is weakened by {sleep}h duration")
    if steps < 8000:
        key_issues.append(f"Daily steps ({int(steps)}) are below optimal activity levels")
        recommendations.append("Add a 20-30 minute walk to increase daily movement")
        daily.append("Take a 15-minute walk after lunch")
        reasoning_parts.append(f"steps at {int(steps)} indicate low activity")
        stress_parts.append(f"low activity ({int(steps)} steps) may contribute to stress")
        fatigue_parts.append(f"low movement ({int(steps)} steps) can increase fatigue")
        wellness_parts.append(f"activity score hurt by only {int(steps)} steps")
    if stress.lower() in ("high", "moderate"):
        key_issues.append(f"Elevated stress level detected ({stress})")
        recommendations.append("Try 5-10 minutes of deep breathing or light stretching today")
        daily.append("Practice 5 minutes of box breathing")
        reasoning_parts.append(f"ML stress prediction is {stress}")
        stress_parts.append(f"model predicts {stress} stress from your wearable pattern")
    if fatigue == 1:
        key_issues.append(f"Fatigue detected ({predictions.get('fatigue_type', 'general')})")
        recommendations.append("Prioritize recovery: hydrate well and consider a lighter workout")
        weekly.append("Schedule 2 rest days this week")
        reasoning_parts.append("fatigue model flagged recovery need")
        fatigue_parts.append(
            f"fatigue type: {predictions.get('fatigue_type', 'general')} — prioritize recovery"
        )
    if readiness < 60:
        wellness_parts.append(f"low readiness ({readiness}/100) is dragging wellness down")

    comparison = (sessions or {}).get("comparison")
    if comparison and comparison.get("feature_changes"):
        change = comparison["feature_changes"][0]
        weekly.append(change["message"])
        reasoning_parts.append("recent session comparison shows metric shifts")

    if not key_issues:
        key_issues.append("No major concerns detected in current metrics")
    if not recommendations:
        recommendations.append("Maintain your current sleep, activity, and recovery routine")

    if score < 40 or (fatigue == 1 and stress.lower() == "high"):
        risk_level = "High"
    elif score < 70 or fatigue == 1 or stress.lower() == "high":
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "summary": (
            f"Your wellness score is {score}/100 with {stress.lower()} stress. "
            + ("Focus on recovery." if fatigue == 1 else "Keep up healthy habits.")
        ),
        "stress_explanation": (
            " ".join(stress_parts)
            if stress_parts
            else f"Stress is {stress} based on your current sleep, heart rate, and activity pattern."
        ),
        "fatigue_explanation": (
            " ".join(fatigue_parts)
            if fatigue_parts
            else (
                "No fatigue detected — your recovery signals look adequate."
                if fatigue == 0
                else "Fatigue detected — review sleep and activity balance."
            )
        ),
        "wellness_explanation": (
            " ".join(wellness_parts)
            if wellness_parts
            else f"Overall wellness at {score}/100 reflects your combined sleep, activity, stress, and recovery."
        ),
        "key_issues": key_issues[:4],
        "recommendations": recommendations[:5],
        "risk_level": risk_level,
        "reasoning": (
            "Recommendations based on: " + ", ".join(reasoning_parts)
            if reasoning_parts
            else "Metrics are within healthy ranges based on current wearable data."
        ),
        "daily_suggestions": daily[:3] or ["Maintain hydration and light movement today"],
        "weekly_suggestions": weekly[:3] or ["Track sleep and steps consistently this week"],
        "is_positive": False,
    }


def _parse_llm_response(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    parsed = json.loads(cleaned)
    return {
        "summary": str(parsed.get("summary", "")),
        "stress_explanation": str(parsed.get("stress_explanation", "")),
        "fatigue_explanation": str(parsed.get("fatigue_explanation", "")),
        "wellness_explanation": str(parsed.get("wellness_explanation", "")),
        "key_issues": list(parsed.get("key_issues", [])),
        "recommendations": list(parsed.get("recommendations", [])),
        "risk_level": str(parsed.get("risk_level", "Medium")),
        "reasoning": str(parsed.get("reasoning", "")),
        "daily_suggestions": list(parsed.get("daily_suggestions", [])),
        "weekly_suggestions": list(parsed.get("weekly_suggestions", [])),
        "is_positive": bool(parsed.get("is_positive", False)),
    }


def _call_gemini(user_prompt: str) -> dict[str, Any]:
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    preferred = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    fallbacks = [preferred, "gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    models_to_try = []
    for name in fallbacks:
        if name and name not in models_to_try:
            models_to_try.append(name)

    genai.configure(api_key=api_key)
    last_error: Exception | None = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(
                model_name,
                system_instruction=SYSTEM_PROMPT,
            )
            response = model.generate_content(
                user_prompt,
                generation_config={
                    "temperature": 0.7,
                    "response_mime_type": "application/json",
                },
            )
            result = _parse_llm_response(response.text or "")
            result["llm_source"] = f"gemini:{model_name}"
            return result
        except Exception as exc:
            last_error = exc
            continue
    if last_error:
        raise last_error
    raise RuntimeError("No Gemini model available")


def _call_openrouter(user_prompt: str) -> dict[str, Any]:
    from openai import OpenAI

    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    preferred = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
    fallbacks = [
        preferred,
        "google/gemini-2.0-flash-exp:free",
        "google/gemini-flash-1.5-8b",
        "openai/gpt-4o-mini",
    ]
    models_to_try = []
    for name in fallbacks:
        if name and name not in models_to_try:
            models_to_try.append(name)

    client = OpenAI(
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=api_key,
    )
    last_error: Exception | None = None
    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or ""
            result = _parse_llm_response(content)
            result["llm_source"] = f"openrouter:{model}"
            return result
        except Exception as exc:
            last_error = exc
            continue
    if last_error:
        raise last_error
    raise RuntimeError("No OpenRouter model available")


def _call_openai(user_prompt: str) -> dict[str, Any]:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "").strip())
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or ""
    result = _parse_llm_response(content)
    result["llm_source"] = f"openai:{os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}"
    return result


def generate_recommendation(
    health_data: dict[str, Any],
    predictions: dict[str, Any],
    wellness: dict[str, Any],
    sessions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    user_prompt = _build_user_prompt(health_data, predictions, wellness, sessions)
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    if openrouter_key and openrouter_key.startswith("sk-or-"):
        try:
            return _call_openrouter(user_prompt)
        except Exception:
            pass

    if gemini_key and gemini_key != "your_gemini_api_key_here":
        try:
            return _call_gemini(user_prompt)
        except Exception:
            pass

    if openai_key and openai_key not in ("", "YOUR_KEY", "your_openai_api_key_here"):
        try:
            return _call_openai(user_prompt)
        except Exception:
            pass

    result = _mock_recommendation(health_data, predictions, wellness, sessions)
    result["llm_source"] = "rule-based-fallback"
    return result
