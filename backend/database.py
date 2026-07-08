import json
import os
import random
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Iterator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "health.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 30000;")
    return conn


@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS wearable_readings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            avg_hr REAL,
            rhr REAL,
            sleep_duration_h REAL,
            deep_sleep_in_minutes REAL,
            steps REAL,
            exercise_duration REAL,
            stress REAL,
            readiness REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT NOT NULL,
            stress TEXT NOT NULL,
            fatigue INTEGER NOT NULL,
            fatigue_type TEXT NOT NULL,
            wellness_score REAL NOT NULL,
            sleep_duration_h REAL,
            steps REAL,
            avg_hr REAL,
            rhr REAL,
            deep_sleep_in_minutes REAL,
            exercise_duration REAL,
            stress_input REAL,
            readiness REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS recommendations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT NOT NULL,
            summary TEXT NOT NULL,
            key_issues TEXT NOT NULL,
            recommendations TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            reasoning TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS assessment_sessions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            avg_hr REAL,
            rhr REAL,
            sleep_duration_h REAL,
            deep_sleep_in_minutes REAL,
            steps REAL,
            exercise_duration REAL,
            stress_input REAL,
            readiness REAL,
            activity_level TEXT,
            stress_feature_sleep REAL,
            stress_feature_activity REAL,
            stress_feature_history REAL,
            stress_feature_hr REAL,
            stress_prediction TEXT NOT NULL,
            fatigue INTEGER NOT NULL,
            fatigue_type TEXT NOT NULL,
            wellness_score REAL NOT NULL,
            risk_score TEXT,
            explanation_json TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    _migrate_columns(cursor)
    _ensure_users_schema(cursor)
    _fix_stale_foreign_keys(cursor)
    _seed_existing_users_without_data(cursor)
    conn.commit()
    conn.close()


def _ensure_users_schema(cursor: sqlite3.Cursor) -> None:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        return

    cursor.execute("PRAGMA table_info(users)")
    cols = {row[1] for row in cursor.fetchall()}
    if "id" in cols:
        if "created_at" not in cols:
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TEXT NOT NULL DEFAULT ''")
        return

    if "user_id" in cols:
        cursor.execute("ALTER TABLE users RENAME TO users_legacy")
        cursor.execute(
            """
            CREATE TABLE users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def _fk_target_table(cursor: sqlite3.Cursor, table: str) -> str | None:
    cursor.execute(f"PRAGMA foreign_key_list({table})")
    rows = cursor.fetchall()
    return rows[0][2] if rows else None


def _fix_stale_foreign_keys(cursor: sqlite3.Cursor) -> None:
    """Rebuild tables that still reference the old users_legacy schema."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        return

    if _fk_target_table(cursor, "wearable_readings") == "users_legacy":
        _rebuild_table(
            cursor,
            "wearable_readings",
            """
            CREATE TABLE wearable_readings(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                avg_hr REAL,
                rhr REAL,
                sleep_duration_h REAL,
                deep_sleep_in_minutes REAL,
                steps REAL,
                exercise_duration REAL,
                stress REAL,
                readiness REAL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """,
            """
            INSERT INTO wearable_readings
            SELECT w.id, w.user_id, w.date, w.avg_hr, w.rhr, w.sleep_duration_h,
                   w.deep_sleep_in_minutes, w.steps, w.exercise_duration, w.stress, w.readiness
            FROM wearable_readings_old w
            INNER JOIN users u ON w.user_id = u.id
            """,
        )

    cursor.execute("PRAGMA table_info(predictions)")
    pred_cols = {row[1] for row in cursor.fetchall()}
    pred_fk_legacy = _fk_target_table(cursor, "predictions") == "users_legacy"
    pred_wrong_pk = "prediction_id" in pred_cols and "id" not in pred_cols
    if pred_fk_legacy or pred_wrong_pk:
        _rebuild_table(
            cursor,
            "predictions",
            """
            CREATE TABLE predictions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT NOT NULL,
                stress TEXT NOT NULL,
                fatigue INTEGER NOT NULL,
                fatigue_type TEXT NOT NULL,
                wellness_score REAL NOT NULL,
                sleep_duration_h REAL,
                steps REAL,
                avg_hr REAL,
                rhr REAL,
                deep_sleep_in_minutes REAL,
                exercise_duration REAL,
                stress_input REAL,
                readiness REAL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """,
            """
            INSERT INTO predictions
            (id, user_id, date, stress, fatigue, fatigue_type, wellness_score,
             sleep_duration_h, steps, avg_hr, rhr, deep_sleep_in_minutes,
             exercise_duration, stress_input, readiness)
            SELECT p.prediction_id, p.user_id, p.date, p.stress, p.fatigue, p.fatigue_type,
                   p.wellness_score, p.sleep_duration_h, p.steps, p.avg_hr, p.rhr,
                   p.deep_sleep_in_minutes, p.exercise_duration, p.stress_input, p.readiness
            FROM predictions_old p
            INNER JOIN users u ON p.user_id = u.id
            """,
        )

    if _fk_target_table(cursor, "recommendations") == "users_legacy":
        _rebuild_table(
            cursor,
            "recommendations",
            """
            CREATE TABLE recommendations(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT NOT NULL,
                summary TEXT NOT NULL,
                key_issues TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                reasoning TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """,
            """
            INSERT INTO recommendations
            SELECT r.id, r.user_id, r.date, r.summary, r.key_issues, r.recommendations,
                   r.risk_level, r.reasoning
            FROM recommendations_old r
            INNER JOIN users u ON r.user_id = u.id
            """,
        )


def _rebuild_table(
    cursor: sqlite3.Cursor,
    table: str,
    create_sql: str,
    copy_sql: str,
) -> None:
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
    if not cursor.fetchone():
        cursor.execute(create_sql)
        return

    cursor.execute(f"ALTER TABLE {table} RENAME TO {table}_old")
    cursor.execute(create_sql)
    cursor.execute(copy_sql)
    cursor.execute(f"DROP TABLE {table}_old")


def _seed_existing_users_without_data(cursor: sqlite3.Cursor) -> None:
    rows = cursor.execute(
        """
        SELECT u.id FROM users u
        LEFT JOIN wearable_readings w ON w.user_id = u.id
        GROUP BY u.id
        HAVING COUNT(w.id) = 0
        """
    ).fetchall()
    conn = cursor.connection
    for row in rows:
        _seed_mock_wearable_data(conn, row[0])


def _migrate_columns(cursor: sqlite3.Cursor) -> None:
    cursor.execute("PRAGMA table_info(users)")
    user_cols = {row[1] for row in cursor.fetchall()}
    for col, typ in {
        "age": "INTEGER",
        "gender": "TEXT",
        "weight_kg": "REAL",
        "height_cm": "REAL",
        "activity_level": "TEXT",
        "sleep_goal_h": "REAL",
    }.items():
        if col not in user_cols:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {typ}")

    cursor.execute("PRAGMA table_info(predictions)")
    pred_cols = {row[1] for row in cursor.fetchall()}
    migrations = {
        "user_id": "INTEGER",
        "sleep_duration_h": "REAL",
        "steps": "REAL",
        "avg_hr": "REAL",
        "rhr": "REAL",
        "deep_sleep_in_minutes": "REAL",
        "exercise_duration": "REAL",
        "stress_input": "REAL",
        "readiness": "REAL",
    }
    for col, typ in migrations.items():
        if col not in pred_cols:
            cursor.execute(f"ALTER TABLE predictions ADD COLUMN {col} {typ}")

    if "stress_level" in pred_cols and "stress" not in pred_cols:
        cursor.execute("ALTER TABLE predictions RENAME COLUMN stress_level TO stress")

    cursor.execute("PRAGMA table_info(recommendations)")
    rec_cols = {row[1] for row in cursor.fetchall()}
    for col, typ in {"user_id": "INTEGER", "reasoning": "TEXT"}.items():
        if col not in rec_cols:
            cursor.execute(f"ALTER TABLE recommendations ADD COLUMN {col} {typ}")


def create_user(
    email: str,
    name: str,
    password_hash: str,
    *,
    age: int | None = None,
    gender: str | None = None,
    weight_kg: float | None = None,
    height_cm: float | None = None,
    activity_level: str | None = None,
    sleep_goal_h: float | None = None,
) -> dict[str, Any]:
    with db_session() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO users
                (email, name, password_hash, created_at, age, gender, weight_kg,
                 height_cm, activity_level, sleep_goal_h)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    email.lower().strip(),
                    name.strip(),
                    password_hash,
                    datetime.now().isoformat(),
                    age,
                    gender,
                    weight_kg,
                    height_cm,
                    activity_level,
                    sleep_goal_h,
                ),
            )
            user_id = cursor.lastrowid
        except sqlite3.IntegrityError as exc:
            raise ValueError("Email already registered") from exc
        _seed_mock_wearable_data(conn, user_id)
        row = conn.execute(
            """
            SELECT id, email, name, created_at, age, gender, weight_kg,
                   height_cm, activity_level, sleep_goal_h
            FROM users WHERE id = ?
            """,
            (user_id,),
        ).fetchone()
        return dict(row)


def get_user_by_email(email: str) -> dict[str, Any] | None:
    conn = get_connection()
    row = conn.execute(
        """
        SELECT id, email, name, password_hash, created_at, age, gender, weight_kg,
               height_cm, activity_level, sleep_goal_h
        FROM users WHERE email = ?
        """,
        (email.lower().strip(),),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict[str, Any]:
    conn = get_connection()
    row = conn.execute(
        """
        SELECT id, email, name, created_at, age, gender, weight_kg,
               height_cm, activity_level, sleep_goal_h
        FROM users WHERE id = ?
        """,
        (user_id,),
    ).fetchone()
    conn.close()
    if not row:
        raise ValueError("User not found")
    return dict(row)


def _public_user(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "email": row["email"],
        "name": row["name"],
        "age": row.get("age"),
        "gender": row.get("gender"),
        "weight_kg": row.get("weight_kg"),
        "height_cm": row.get("height_cm"),
        "activity_level": row.get("activity_level"),
        "sleep_goal_h": row.get("sleep_goal_h"),
    }


def save_wearable_reading(user_id: int, data: dict[str, Any]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO wearable_readings
        (user_id, date, avg_hr, rhr, sleep_duration_h, deep_sleep_in_minutes,
         steps, exercise_duration, stress, readiness)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            datetime.now().isoformat(),
            data["avg_hr"],
            data["rhr"],
            data["sleep_duration_h"],
            data["deep_sleep_in_minutes"],
            data["steps"],
            data["exercise_duration"],
            data["stress"],
            data["readiness"],
        ),
    )
    reading_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return reading_id


def get_wearable_readings(user_id: int, days: int | None = None) -> list[dict[str, Any]]:
    conn = get_connection()
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        rows = conn.execute(
            """
            SELECT * FROM wearable_readings
            WHERE user_id = ? AND date >= ?
            ORDER BY date ASC
            """,
            (user_id, cutoff),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM wearable_readings WHERE user_id = ? ORDER BY date ASC",
            (user_id,),
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_prediction(user_id: int, stress: str, fatigue: int, fatigue_type: str, wellness_score: float, data: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO predictions
        (user_id, date, stress, fatigue, fatigue_type, wellness_score,
         sleep_duration_h, steps, avg_hr, rhr, deep_sleep_in_minutes,
         exercise_duration, stress_input, readiness)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            datetime.now().isoformat(),
            stress,
            fatigue,
            fatigue_type,
            wellness_score,
            data.get("sleep_duration_h"),
            data.get("steps"),
            data.get("avg_hr"),
            data.get("rhr"),
            data.get("deep_sleep_in_minutes"),
            data.get("exercise_duration"),
            data.get("stress"),
            data.get("readiness"),
        ),
    )
    prediction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return prediction_id


def get_predictions(user_id: int) -> list[dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, date, stress, fatigue, fatigue_type, wellness_score,
               sleep_duration_h, steps, avg_hr, rhr, stress_input,
               exercise_duration, deep_sleep_in_minutes, readiness
        FROM predictions WHERE user_id = ?
        ORDER BY date DESC
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_latest_prediction(user_id: int) -> dict[str, Any] | None:
    items = get_predictions(user_id)
    return items[0] if items else None


def delete_prediction(user_id: int, prediction_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM predictions WHERE id = ? AND user_id = ?",
        (prediction_id, user_id),
    )
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def save_recommendation(
    user_id: int,
    summary: str,
    key_issues: list[str],
    recommendations: list[str],
    risk_level: str,
    reasoning: str = "",
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO recommendations
        (user_id, date, summary, key_issues, recommendations, risk_level, reasoning)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            datetime.now().isoformat(),
            summary,
            "|".join(key_issues),
            "|".join(recommendations),
            risk_level,
            reasoning,
        ),
    )
    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rec_id


def get_recommendations(user_id: int) -> list[dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, date, summary, key_issues, recommendations, risk_level, reasoning
        FROM recommendations WHERE user_id = ?
        ORDER BY date DESC
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    result = []
    for row in rows:
        item = dict(row)
        item["key_issues"] = item["key_issues"].split("|") if item["key_issues"] else []
        item["recommendations"] = item["recommendations"].split("|") if item["recommendations"] else []
        result.append(item)
    return result


def save_assessment_session(
    user_id: int,
    payload: dict[str, Any],
    stress_features: dict[str, float],
    predictions: dict[str, Any],
    wellness_score: float,
    risk_score: str,
    explanation: dict[str, Any],
    activity_level: str | None = None,
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO assessment_sessions
        (user_id, created_at, avg_hr, rhr, sleep_duration_h, deep_sleep_in_minutes,
         steps, exercise_duration, stress_input, readiness, activity_level,
         stress_feature_sleep, stress_feature_activity, stress_feature_history,
         stress_feature_hr, stress_prediction, fatigue, fatigue_type, wellness_score,
         risk_score, explanation_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            datetime.now().isoformat(),
            payload.get("avg_hr"),
            payload.get("rhr"),
            payload.get("sleep_duration_h"),
            payload.get("deep_sleep_in_minutes"),
            payload.get("steps"),
            payload.get("exercise_duration"),
            payload.get("stress"),
            payload.get("readiness"),
            activity_level,
            stress_features.get("sleep_duration_h"),
            stress_features.get("activity_level"),
            stress_features.get("stress_history"),
            stress_features.get("avg_hr"),
            predictions["stress"],
            predictions["fatigue"],
            predictions["fatigue_type"],
            wellness_score,
            risk_score,
            json.dumps(explanation),
        ),
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def get_assessment_sessions(user_id: int, limit: int = 50) -> list[dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM assessment_sessions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_average_physiological_load(user_id: int) -> float | None:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT avg_hr, rhr, sleep_duration_h, steps, deep_sleep_in_minutes
        FROM assessment_sessions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 10
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    if not rows:
        return None
    from model_features import compute_physiological_load

    loads = [
        compute_physiological_load(
            avg_hr=row[0] or 70,
            rhr=row[1] or 58,
            sleep_duration_h=row[2] or 7,
            steps=row[3] or 8000,
            deep_sleep_in_minutes=row[4] or 90,
        )
        for row in rows
    ]
    return round(sum(loads) / len(loads), 1)


def get_average_stress_history(user_id: int) -> float | None:
    """Deprecated alias — kept for compatibility."""
    return get_average_physiological_load(user_id)


def seed_mock_wearable_data(user_id: int, days: int = 21) -> None:
    with db_session() as conn:
        _seed_mock_wearable_data(conn, user_id, days)


def _seed_mock_wearable_data(conn: sqlite3.Connection, user_id: int, days: int = 21) -> None:
    existing = conn.execute(
        "SELECT COUNT(*) FROM wearable_readings WHERE user_id = ?",
        (user_id,),
    ).fetchone()[0]
    if existing > 0:
        return

    cursor = conn.cursor()
    base = datetime.now()
    for i in range(days, 0, -1):
        day = base - timedelta(days=i)
        cursor.execute(
            """
            INSERT INTO wearable_readings
            (user_id, date, avg_hr, rhr, sleep_duration_h, deep_sleep_in_minutes,
             steps, exercise_duration, stress, readiness)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                day.isoformat(),
                round(random.uniform(65, 85), 1),
                round(random.uniform(52, 65), 1),
                round(random.uniform(6.0, 8.5), 1),
                round(random.uniform(60, 110), 1),
                round(random.uniform(5000, 12000), 0),
                round(random.uniform(20, 60), 1),
                round(random.uniform(20, 70), 1),
                round(random.uniform(55, 90), 1),
            ),
        )
