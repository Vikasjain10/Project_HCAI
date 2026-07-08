import os

from typing import Literal

import joblib
import pandas as pd
import sqlite3
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

from wellness_engine import (
    calculate_heart_score,
    calculate_sleep_score,
    calculate_activity_score,
    calculate_stress_score,
    calculate_recovery_score,
    calculate_wellness_score,
    wellness_category
)

from auth import create_access_token, get_current_user, hash_password, verify_password
from database import (
    create_user,
    delete_prediction,
    get_assessment_sessions,
    get_average_physiological_load,
    get_latest_prediction,
    get_predictions,
    get_recommendations,
    get_user_by_email,
    get_wearable_readings,
    init_db,
    save_assessment_session,
    save_prediction,
    save_recommendation,
    save_wearable_reading,
    _public_user,
)
from explain_service import build_all_explanations, explain_fatigue, explain_prediction
from llm_service import generate_recommendation
from model_features import build_fatigue_features, build_stress_features, build_stress_model_features
from session_service import build_session_comparison
from trends_service import build_trends, compute_trend_deltas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

app = FastAPI(title="HCAI Health Monitoring API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stress_model = None
fatigue_model = None
fatigue_type_model = None


def _load_models() -> None:
    global stress_model, fatigue_model, fatigue_type_model
    required = {
        "stress_model.pkl": "stress",
        "fatigue_model.pkl": "fatigue",
        "fatigue_type_model.pkl": "fatigue type",
    }
    missing = [name for name in required if not os.path.isfile(os.path.join(MODEL_DIR, name))]
    if missing:
        raise RuntimeError(
            f"Missing model files in {MODEL_DIR}: {', '.join(missing)}. "
            "Run the training scripts in backend/ or copy pre-trained .pkl files."
        )
    stress_model = joblib.load(os.path.join(MODEL_DIR, "stress_model.pkl"))
    fatigue_model = joblib.load(os.path.join(MODEL_DIR, "fatigue_model.pkl"))
    fatigue_type_model = joblib.load(os.path.join(MODEL_DIR, "fatigue_type_model.pkl"))


class SignupRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=6, max_length=128)
    age: int = Field(ge=13, le=120)
    gender: Literal["male", "female", "other", "prefer_not_to_say"]
    weight_kg: float = Field(ge=20, le=300)
    height_cm: float = Field(ge=100, le=250)
    activity_level: Literal["sedentary", "moderate", "active"]
    sleep_goal_h: float = Field(ge=4, le=12)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class HealthInput(BaseModel):
    avg_hr: float = Field(ge=40, le=200)
    rhr: float = Field(ge=30, le=120)
    sleep_duration_h: float = Field(ge=0, le=16)
    deep_sleep_in_minutes: float = Field(ge=0, le=300)
    steps: float = Field(ge=0, le=50000)
    exercise_duration: float = Field(ge=0, le=300)
    stress: float = Field(ge=0, le=100)
    readiness: float = Field(ge=0, le=100)


class PredictionsOutput(BaseModel):
    stress: str
    fatigue: int
    fatigue_type: str


class WellnessOutput(BaseModel):
    score: float
    breakdown: dict[str, float] | None = None
    category: str | None = None


class RecommendationInput(BaseModel):
    avg_hr: float
    rhr: float
    sleep_duration_h: float
    deep_sleep_in_minutes: float
    steps: float
    exercise_duration: float
    stress: float
    readiness: float
    predictions: PredictionsOutput
    wellness: WellnessOutput



def calculate_wellness(data: HealthInput):

    heart = calculate_heart_score(
        data.avg_hr,
        data.rhr
    )

    sleep = calculate_sleep_score(
        data.sleep_duration_h,
        data.deep_sleep_in_minutes
    )

    activity = calculate_activity_score(
        data.steps,
        data.exercise_duration
    )

    stress = calculate_stress_score(
        data.stress
    )

    recovery = calculate_recovery_score(
        data.readiness,
        data.rhr
    )

    score = calculate_wellness_score(
        heart,
        sleep,
        activity,
        stress,
        recovery
    )

    category = wellness_category(score)

    return {
        "score": score,
        "category": category,
        "heart_score": heart,
        "sleep_score": sleep,
        "activity_score": activity,
        "stress_score": stress,
        "recovery_score": recovery
    }


def run_predictions(data: HealthInput) -> dict:
    

    # ---------------- STRESS FEATURES ----------------

    stress_features = pd.DataFrame([{
        "avg_hr": data.avg_hr,
        "rhr": data.rhr,
        "deep_sleep_in_minutes": data.deep_sleep_in_minutes,
        "minutes_asleep": data.sleep_duration_h * 60,
        "steps": data.steps,
        "exercise_duration": data.exercise_duration,
        "overall_score":
            ((data.sleep_duration_h / 8) * 50) +
            ((data.deep_sleep_in_minutes / 120) * 50),
        "restlessness":
            max(0, 1 - (data.deep_sleep_in_minutes / 120))
    }])

    # ---------------- FATIGUE FEATURES ----------------

    fatigue_features = pd.DataFrame([{
        "avg_hr": data.avg_hr,
        "rhr": data.rhr,
        "sleep_duration_h": data.sleep_duration_h,
        "deep_sleep_in_minutes": data.deep_sleep_in_minutes,
        "steps": data.steps,
        "exercise_duration": data.exercise_duration,
        "stress": data.stress,
        "readiness": data.readiness
    }])

    # --------------------------------------------------
    # STRESS PREDICTION
    # --------------------------------------------------

    stress = stress_model.predict(stress_features)[0]

    # Physiological override for stress
    stress_risk = 0

    if data.avg_hr > 90:
        stress_risk += 2

    if data.sleep_duration_h < 5:
        stress_risk += 3

    if data.steps < 1000:
        stress_risk += 2

    if data.readiness < 40:
        stress_risk += 3

    # Only increase stress level when body signals are clearly poor
    if stress_risk >= 7:
        stress = "High"

    elif stress_risk >= 4 and str(stress).lower() == "low":
        stress = "Moderate"


    # --------------------------------------------------
    # FATIGUE PREDICTION
    # --------------------------------------------------

    probability = fatigue_model.predict_proba(fatigue_features)[0][1]

    fatigue = 1 if probability >= 0.60 else 0

    # Physiological validation
    if (
        data.avg_hr < 85
        and data.rhr < 65
        and data.sleep_duration_h >= 7
        and data.deep_sleep_in_minutes >= 80
        and data.readiness >= 70
    ):
        fatigue = 0

    # Force fatigue if body condition is clearly poor
    fatigue_risk = 0

    if data.avg_hr > 90:
        fatigue_risk += 2

    if data.sleep_duration_h < 5:
        fatigue_risk += 3

    if data.steps < 1000:
        fatigue_risk += 2

    if data.exercise_duration == 0:
        fatigue_risk += 1

    if data.readiness < 40:
        fatigue_risk += 3

    if fatigue_risk >= 6:
        fatigue = 1


    # --------------------------------------------------
    # FATIGUE TYPE
    # --------------------------------------------------

    if fatigue == 1:
        fatigue_type = fatigue_type_model.predict(fatigue_features)[0]
    else:
        fatigue_type = "No Fatigue"


    # --------------------------------------------------
    # WELLNESS
    # --------------------------------------------------

    wellness = calculate_wellness(data)

    return {
        "predictions": {
            "stress": str(stress),
            "fatigue": fatigue,
            "fatigue_type": str(fatigue_type)
        },
        "wellness": wellness
    }


def _wellness_breakdown(wellness: dict) -> dict[str, float]:
    return {
        "sleep": wellness["sleep_score"],
        "activity": wellness["activity_score"],
        "recovery": wellness["recovery_score"],
        "stress_control": wellness["stress_score"],
        "exercise": wellness["activity_score"],
    }


def _build_explanations(payload: dict, result: dict) -> dict:
    stress_features = build_stress_model_features(payload)
    fatigue_features = build_fatigue_features(payload)
    wellness = result["wellness"]
    return build_all_explanations(
        stress_features=stress_features,
        fatigue_features=fatigue_features,
        stress_label=result["predictions"]["stress"],
        fatigue=result["predictions"]["fatigue"],
        wellness_breakdown=_wellness_breakdown(wellness),
        wellness_score=wellness["score"],
    )

def _risk_score(predictions: dict, wellness: dict) -> str:
    stress = str(predictions.get("stress", "")).lower()
    score = wellness.get("score", 50)
    fatigue = predictions.get("fatigue", 0)
    if fatigue == 1 and stress == "high":
        return "High"
    if score < 50 or stress == "high" or fatigue == 1:
        return "Medium"
    return "Low"


@app.on_event("startup")
def startup() -> None:
    init_db()
    _load_models()


@app.get("/")
def root():
    return {"message": "HCAI Health Monitoring API", "status": "running"}


@app.post("/auth/signup")
def signup(data: SignupRequest):
    try:
        user = create_user(
            data.email,
            data.name,
            hash_password(data.password),
            age=data.age,
            gender=data.gender,
            weight_kg=data.weight_kg,
            height_cm=data.height_cm,
            activity_level=data.activity_level,
            sleep_goal_h=data.sleep_goal_h,
        )
        token = create_access_token(user["id"], user["email"], user["name"])
        return {"token": token, "user": _public_user(user)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Email already registered") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {e}") from e


@app.post("/auth/login")
def login(data: LoginRequest):
    user = get_user_by_email(data.email)
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user["id"], user["email"], user["name"])
    return {"token": token, "user": _public_user(user)}


@app.get("/auth/me")
def me(user=Depends(get_current_user)):
    return user


def _summary_from_latest(user: dict, latest: dict, weekly: dict, session_count: int) -> dict:
    return {
        "health_status": latest["stress"],
        "risk_score": _risk_score(
            {"stress": latest["stress"], "fatigue": latest["fatigue"]},
            {"score": latest["wellness_score"]},
        ),
        "wellness_score": latest["wellness_score"],
        "fatigue": latest["fatigue"],
        "last_updated": latest["date"],
        "has_data": weekly["has_data"],
        "sleep_hours": latest.get("sleep_duration_h"),
        "stress_score": latest.get("stress_input"),
        "activity_steps": latest.get("steps"),
        "session_count": session_count,
        "sleep_goal_h": user.get("sleep_goal_h"),
        "activity_level": user.get("activity_level"),
    }


@app.get("/dashboard/summary")
def dashboard_summary(user=Depends(get_current_user)):
    latest = get_latest_prediction(user["id"])
    readings = get_wearable_readings(user["id"])
    weekly = build_trends(readings, 7)
    session_count = len(get_assessment_sessions(user["id"], limit=500))
    if latest:
        return _summary_from_latest(user, latest, weekly, session_count)
    if readings:
        last = readings[-1]
        return {
            "health_status": "Pending assessment",
            "risk_score": "Unknown",
            "wellness_score": None,
            "last_updated": last["date"],
            "has_data": True,
            "sleep_hours": last.get("sleep_duration_h"),
            "stress_score": last.get("stress"),
            "activity_steps": last.get("steps"),
            "session_count": session_count,
            "sleep_goal_h": user.get("sleep_goal_h"),
            "activity_level": user.get("activity_level"),
        }
    return {
        "health_status": "No data",
        "risk_score": "Unknown",
        "wellness_score": None,
        "last_updated": None,
        "has_data": False,
        "sleep_hours": None,
        "stress_score": None,
        "activity_steps": None,
        "session_count": session_count,
        "sleep_goal_h": user.get("sleep_goal_h"),
        "activity_level": user.get("activity_level"),
    }


@app.get("/wearable/history")
def wearable_history(days: int = 30, user=Depends(get_current_user)):
    readings = get_wearable_readings(user["id"])
    weekly = build_trends(readings, 7)
    monthly = build_trends(readings, 30)
    filtered = build_trends(readings, days)
    deltas = compute_trend_deltas(weekly, monthly)
    return {
        "readings": get_wearable_readings(user["id"], days) if days else readings,
        "weekly": weekly,
        "monthly": monthly,
        "selected_range": filtered,
        "deltas": deltas,
    }


@app.get("/sessions/history")
def sessions_history(limit: int = 14, user=Depends(get_current_user)):
    sessions = get_assessment_sessions(user["id"], limit=limit)
    return build_session_comparison(sessions)


@app.post("/full_assessment")
def full_assessment(data: HealthInput, user=Depends(get_current_user)):
    try:
        result = run_predictions(data)
        payload = data.model_dump()
        risk = _risk_score(result["predictions"], result["wellness"])
        explanations = _build_explanations(payload, result)
        save_wearable_reading(user["id"], payload)
        save_prediction(
            user["id"],
            result["predictions"]["stress"],
            result["predictions"]["fatigue"],
            result["predictions"]["fatigue_type"],
            result["wellness"]["score"],
            payload,
        )
        stress_for_session = build_stress_features(
            sleep_duration_h=data.sleep_duration_h,
            avg_hr=data.avg_hr,
            rhr=data.rhr,
            steps=data.steps,
            deep_sleep_in_minutes=data.deep_sleep_in_minutes,
            activity_level=user.get("activity_level"),
            prior_physiological_load=get_average_physiological_load(user["id"]),
        )
        save_assessment_session(
            user["id"],
            payload,
            stress_for_session,
            result["predictions"],
            result["wellness"]["score"],
            risk,
            explanations,
            activity_level=user.get("activity_level"),
        )
        wearable_fatigue = {
            key: build_fatigue_features(payload)[key]
            for key in ("avg_hr", "rhr", "sleep_duration_h", "deep_sleep_in_minutes", "steps", "exercise_duration")
        }
        wellness = {
            **result["wellness"],
            "breakdown": _wellness_breakdown(result["wellness"]),
        }
        return {
            **result,
            "wellness": wellness,
            "stress_features": stress_for_session,
            "fatigue_features": wearable_fatigue,
            "explanations": explanations,
            "explanation": explanations["stress"],
            "risk_score": risk,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/explain")
def explain(data: HealthInput, user=Depends(get_current_user)):
    result = run_predictions(data)
    explanations = _build_explanations(data.model_dump(), result)
    return explanations


@app.post("/recommendation")
def recommendation(data: RecommendationInput, user=Depends(get_current_user)):
    try:
        health_data = data.model_dump(exclude={"predictions", "wellness"})
        predictions = data.predictions.model_dump()
        wellness = data.wellness.model_dump()

        readings = get_wearable_readings(user["id"])
        weekly = build_trends(readings, 7)
        monthly = build_trends(readings, 30)
        deltas = compute_trend_deltas(weekly, monthly)
        session_data = build_session_comparison(get_assessment_sessions(user["id"], limit=14))

        advice = generate_recommendation(
            health_data,
            predictions,
            wellness,
            sessions=session_data if session_data.get("has_data") else None,
        )

        save_recommendation(
            user["id"],
            advice["summary"],
            advice["key_issues"],
            advice["recommendations"],
            advice["risk_level"],
            advice.get("reasoning", ""),
        )

        explanation = {
            "stress": explain_prediction(
                build_stress_model_features(health_data),
                predictions["stress"],
            ),
            "fatigue": explain_fatigue(
                build_fatigue_features(health_data),
                predictions["fatigue"],
            ),
        }
        return {**advice, "explanation": explanation, "trend_deltas": deltas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/history/predictions")
def history_predictions(user=Depends(get_current_user)):
    return {"items": get_predictions(user["id"])}


@app.delete("/history/predictions/{prediction_id}")
def remove_prediction(prediction_id: int, user=Depends(get_current_user)):
    if not delete_prediction(user["id"], prediction_id):
        raise HTTPException(status_code=404, detail="Prediction not found")
    return {"message": "Deleted successfully"}


@app.get("/history/recommendations")
def history_recommendations(user=Depends(get_current_user)):
    return {"items": get_recommendations(user["id"])}


@app.get("/analytics")
def analytics(days: int = 30, user=Depends(get_current_user)):
    readings = get_wearable_readings(user["id"])
    predictions = get_predictions(user["id"])
    weekly = build_trends(readings, 7)
    monthly = build_trends(readings, min(days, 30))
    return {
        "weekly": weekly,
        "monthly": monthly,
        "sleep_vs_wellness": [
            {"date": p["date"][:10], "sleep": p.get("sleep_duration_h") or 0, "wellness": p["wellness_score"]}
            for p in predictions
        ],
        "stress_distribution": _stress_distribution(predictions),
    }



def _stress_distribution(items: list) -> list[dict]:
    counts: dict[str, int] = {}
    for item in items:
        level = str(item["stress"])
        counts[level] = counts.get(level, 0) + 1
    return [{"stress": k, "count": v} for k, v in counts.items()]