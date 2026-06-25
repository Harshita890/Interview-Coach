import json
import sqlite3
from datetime import datetime
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "interview_mirror.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                candidate_name TEXT NOT NULL,
                role TEXT NOT NULL,
                difficulty TEXT,
                category TEXT,
                question TEXT,
                transcript TEXT NOT NULL,
                recording_name TEXT,
                overall_score INTEGER NOT NULL,
                confidence_score INTEGER NOT NULL,
                communication_score INTEGER NOT NULL,
                sentiment_label TEXT NOT NULL,
                speaking_pace INTEGER NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )


def create_user(name, email, password):
    now = datetime.utcnow().isoformat(timespec="seconds")
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (name, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (name, email.lower(), generate_password_hash(password), now),
        )
        return cursor.lastrowid


def find_user_by_email(email):
    with get_connection() as connection:
        return connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.lower(),),
        ).fetchone()


def verify_user(email, password):
    user = find_user_by_email(email)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


def save_interview_session(result, user_id=None, difficulty=None, category=None, question=None):
    metrics = result["metrics"]
    now = datetime.utcnow().isoformat(timespec="seconds")
    result_json = json.dumps(result)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO interview_sessions (
                user_id, candidate_name, role, difficulty, category, question, transcript,
                recording_name, overall_score, confidence_score, communication_score,
                sentiment_label, speaking_pace, result_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                result["candidate_name"],
                result["role"],
                difficulty,
                category,
                question,
                result["transcript"],
                result.get("recording_name"),
                metrics["overall_score"],
                metrics["confidence_score"],
                metrics["communication_score"],
                result["sentiment"]["label"],
                metrics["speaking_pace"],
                result_json,
                now,
            ),
        )
        return cursor.lastrowid


def list_interview_sessions(user_id=None, limit=50):
    query = """
        SELECT * FROM interview_sessions
    """
    params = []
    if user_id:
        query += " WHERE user_id = ?"
        params.append(user_id)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    with get_connection() as connection:
        return connection.execute(query, params).fetchall()


def get_interview_session(session_id, user_id=None):
    query = "SELECT * FROM interview_sessions WHERE id = ?"
    params = [session_id]
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)

    with get_connection() as connection:
        row = connection.execute(query, params).fetchone()

    if not row:
        return None

    result = dict(row)
    result["analysis"] = json.loads(row["result_json"])
    return result
