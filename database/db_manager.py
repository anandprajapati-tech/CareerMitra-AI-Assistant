# database/db_manager.py
# CareerMitra AI – SQLite Database Manager

import sqlite3
import json
import os
from datetime import datetime
from config.settings import DB_PATH


def get_connection():
    """Return a SQLite connection; create the DB file if it doesn't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # rows as dict-like objects
    return conn


def init_db():
    """Create all required tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # ── Students table ────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    UNIQUE NOT NULL,
            phone       TEXT,
            age         INTEGER,
            city        TEXT,
            education   TEXT,
            stream      TEXT,
            institution TEXT,
            gpa         REAL,
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP,
            updated_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Student skills table ──────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_skills (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id   INTEGER NOT NULL,
            skill_name   TEXT    NOT NULL,
            category     TEXT,
            proficiency  TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)

    # ── Student interests table ───────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_interests (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  INTEGER NOT NULL,
            interest    TEXT    NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)

    # ── Career goals table ────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_goals (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id      INTEGER NOT NULL,
            goal_domain     TEXT,
            target_role     TEXT,
            target_timeline TEXT,
            notes           TEXT,
            created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)

    # ── Counselor sessions table ───────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS counselor_sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  INTEGER NOT NULL,
            role        TEXT    NOT NULL,    -- 'user' or 'assistant'
            message     TEXT    NOT NULL,
            timestamp   TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)

    # ── Recommendations table ─────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id      INTEGER NOT NULL,
            career_domain   TEXT,
            recommended_roles TEXT,
            match_score     REAL,
            reasoning       TEXT,
            created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)

    # ── Progress milestones table ─────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress_milestones (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  INTEGER NOT NULL,
            title       TEXT    NOT NULL,
            category    TEXT,
            completed   INTEGER DEFAULT 0,    -- 0 = pending, 1 = done
            due_date    TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ── Student CRUD ──────────────────────────────────────────────────────────────

def save_student(profile: dict) -> int:
    """Insert or update a student record; return the student ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM students WHERE email = ?", (profile.get("email"),))
    row = cursor.fetchone()

    if row:
        student_id = row["id"]
        cursor.execute("""
            UPDATE students
            SET name=?, phone=?, age=?, city=?, education=?, stream=?,
                institution=?, gpa=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (
            profile.get("name"), profile.get("phone"), profile.get("age"),
            profile.get("city"), profile.get("education"), profile.get("stream"),
            profile.get("institution"), profile.get("gpa"), student_id
        ))
    else:
        cursor.execute("""
            INSERT INTO students (name, email, phone, age, city, education, stream, institution, gpa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.get("name"), profile.get("email"), profile.get("phone"),
            profile.get("age"), profile.get("city"), profile.get("education"),
            profile.get("stream"), profile.get("institution"), profile.get("gpa")
        ))
        student_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return student_id


def get_student_by_email(email: str) -> dict | None:
    """Fetch a student record by email."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_student_by_id(student_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_students() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Skills ────────────────────────────────────────────────────────────────────

def save_skills(student_id: int, skills: list[dict]):
    """Replace all skills for a student."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student_skills WHERE student_id = ?", (student_id,))
    for s in skills:
        cursor.execute(
            "INSERT INTO student_skills (student_id, skill_name, category, proficiency) VALUES (?, ?, ?, ?)",
            (student_id, s.get("name"), s.get("category"), s.get("proficiency"))
        )
    conn.commit()
    conn.close()


def get_skills(student_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_skills WHERE student_id = ?", (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Interests ─────────────────────────────────────────────────────────────────

def save_interests(student_id: int, interests: list[str]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student_interests WHERE student_id = ?", (student_id,))
    for interest in interests:
        cursor.execute(
            "INSERT INTO student_interests (student_id, interest) VALUES (?, ?)",
            (student_id, interest)
        )
    conn.commit()
    conn.close()


def get_interests(student_id: int) -> list[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT interest FROM student_interests WHERE student_id = ?", (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return [r["interest"] for r in rows]


# ── Career Goals ──────────────────────────────────────────────────────────────

def save_career_goal(student_id: int, goal: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM career_goals WHERE student_id = ?", (student_id,))
    cursor.execute("""
        INSERT INTO career_goals (student_id, goal_domain, target_role, target_timeline, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (student_id, goal.get("domain"), goal.get("role"), goal.get("timeline"), goal.get("notes")))
    conn.commit()
    conn.close()


def get_career_goal(student_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM career_goals WHERE student_id = ? ORDER BY created_at DESC LIMIT 1", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ── Counselor Chat History ────────────────────────────────────────────────────

def save_chat_message(student_id: int, role: str, message: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO counselor_sessions (student_id, role, message) VALUES (?, ?, ?)",
        (student_id, role, message)
    )
    conn.commit()
    conn.close()


def get_chat_history(student_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, message, timestamp FROM counselor_sessions WHERE student_id = ? ORDER BY timestamp ASC",
        (student_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def clear_chat_history(student_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM counselor_sessions WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()


# ── Recommendations ───────────────────────────────────────────────────────────

def save_recommendation(student_id: int, rec: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recommendations (student_id, career_domain, recommended_roles, match_score, reasoning)
        VALUES (?, ?, ?, ?, ?)
    """, (
        student_id,
        rec.get("domain"),
        json.dumps(rec.get("roles", [])),
        rec.get("score"),
        rec.get("reasoning")
    ))
    conn.commit()
    conn.close()


def get_latest_recommendation(student_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM recommendations WHERE student_id = ? ORDER BY created_at DESC LIMIT 1",
        (student_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["roles"] = json.loads(d.get("recommended_roles") or "[]")
        return d
    return None


# ── Progress Milestones ───────────────────────────────────────────────────────

def save_milestones(student_id: int, milestones: list[dict]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM progress_milestones WHERE student_id = ?", (student_id,))
    for m in milestones:
        cursor.execute("""
            INSERT INTO progress_milestones (student_id, title, category, completed, due_date)
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, m.get("title"), m.get("category"), int(m.get("completed", False)), m.get("due_date")))
    conn.commit()
    conn.close()


def get_milestones(student_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM progress_milestones WHERE student_id = ? ORDER BY created_at ASC", (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_milestone_status(milestone_id: int, completed: bool):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE progress_milestones SET completed = ? WHERE id = ?",
        (int(completed), milestone_id)
    )
    conn.commit()
    conn.close()
