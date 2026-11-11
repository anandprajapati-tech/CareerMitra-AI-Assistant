# src/database.py
# CareerMitra AI – SQLite Database Manager

import sqlite3
import json
import os
from src.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection, creating the DB file if needed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they do not exist."""
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
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
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS student_skills (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  INTEGER NOT NULL,
            skill_name  TEXT    NOT NULL,
            category    TEXT,
            proficiency TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS student_interests (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  INTEGER NOT NULL,
            interest    TEXT    NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS career_goals (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id      INTEGER NOT NULL,
            goal_domain     TEXT,
            target_role     TEXT,
            target_timeline TEXT,
            notes           TEXT,
            created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS counselor_sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  INTEGER NOT NULL,
            role        TEXT    NOT NULL,
            message     TEXT    NOT NULL,
            timestamp   TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS recommendations (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id        INTEGER NOT NULL,
            career_domain     TEXT,
            recommended_roles TEXT,
            match_score       REAL,
            reasoning         TEXT,
            created_at        TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS progress_milestones (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  INTEGER NOT NULL,
            title       TEXT    NOT NULL,
            category    TEXT,
            completed   INTEGER DEFAULT 0,
            due_date    TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()


# ── Students ──────────────────────────────────────────────────────────────────

def save_student(profile: dict) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM students WHERE email=?", (profile.get("email"),))
    row = c.fetchone()
    if row:
        sid = row["id"]
        c.execute("""
            UPDATE students
            SET name=?,phone=?,age=?,city=?,education=?,stream=?,institution=?,gpa=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (profile.get("name"), profile.get("phone"), profile.get("age"),
              profile.get("city"), profile.get("education"), profile.get("stream"),
              profile.get("institution"), profile.get("gpa"), sid))
    else:
        c.execute("""
            INSERT INTO students (name,email,phone,age,city,education,stream,institution,gpa)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (profile.get("name"), profile.get("email"), profile.get("phone"),
              profile.get("age"), profile.get("city"), profile.get("education"),
              profile.get("stream"), profile.get("institution"), profile.get("gpa")))
        sid = c.lastrowid
    conn.commit()
    conn.close()
    return sid


def get_student_by_id(sid: int) -> dict | None:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE id=?", (sid,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_student_by_email(email: str) -> dict | None:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_students() -> list[dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM students ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Skills ────────────────────────────────────────────────────────────────────

def save_skills(sid: int, skills: list[dict]):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM student_skills WHERE student_id=?", (sid,))
    for s in skills:
        c.execute(
            "INSERT INTO student_skills (student_id,skill_name,category,proficiency) VALUES (?,?,?,?)",
            (sid, s.get("name"), s.get("category"), s.get("proficiency")),
        )
    conn.commit()
    conn.close()


def get_skills(sid: int) -> list[dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM student_skills WHERE student_id=?", (sid,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Interests ─────────────────────────────────────────────────────────────────

def save_interests(sid: int, interests: list[str]):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM student_interests WHERE student_id=?", (sid,))
    for i in interests:
        c.execute("INSERT INTO student_interests (student_id,interest) VALUES (?,?)", (sid, i))
    conn.commit()
    conn.close()


def get_interests(sid: int) -> list[str]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT interest FROM student_interests WHERE student_id=?", (sid,))
    rows = c.fetchall()
    conn.close()
    return [r["interest"] for r in rows]


# ── Career Goals ──────────────────────────────────────────────────────────────

def save_career_goal(sid: int, goal: dict):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM career_goals WHERE student_id=?", (sid,))
    c.execute("""
        INSERT INTO career_goals (student_id,goal_domain,target_role,target_timeline,notes)
        VALUES (?,?,?,?,?)
    """, (sid, goal.get("domain"), goal.get("role"), goal.get("timeline"), goal.get("notes")))
    conn.commit()
    conn.close()


def get_career_goal(sid: int) -> dict | None:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM career_goals WHERE student_id=? ORDER BY created_at DESC LIMIT 1", (sid,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


# ── Counselor Chat ────────────────────────────────────────────────────────────

def save_chat_message(sid: int, role: str, message: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO counselor_sessions (student_id,role,message) VALUES (?,?,?)",
              (sid, role, message))
    conn.commit()
    conn.close()


def get_chat_history(sid: int) -> list[dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT role,message,timestamp FROM counselor_sessions WHERE student_id=? ORDER BY timestamp ASC", (sid,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def clear_chat_history(sid: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM counselor_sessions WHERE student_id=?", (sid,))
    conn.commit()
    conn.close()


# ── Recommendations ───────────────────────────────────────────────────────────

def save_recommendation(sid: int, rec: dict):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO recommendations (student_id,career_domain,recommended_roles,match_score,reasoning)
        VALUES (?,?,?,?,?)
    """, (sid, rec.get("domain"), json.dumps(rec.get("roles", [])), rec.get("score"), rec.get("reasoning")))
    conn.commit()
    conn.close()


def get_latest_recommendation(sid: int) -> dict | None:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM recommendations WHERE student_id=? ORDER BY created_at DESC LIMIT 1", (sid,))
    row = c.fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["roles"] = json.loads(d.get("recommended_roles") or "[]")
        return d
    return None


# ── Milestones ────────────────────────────────────────────────────────────────

def save_milestones(sid: int, milestones: list[dict]):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM progress_milestones WHERE student_id=?", (sid,))
    for m in milestones:
        c.execute("""
            INSERT INTO progress_milestones (student_id,title,category,completed,due_date)
            VALUES (?,?,?,?,?)
        """, (sid, m.get("title"), m.get("category"), int(m.get("completed", False)), m.get("due_date")))
    conn.commit()
    conn.close()


def get_milestones(sid: int) -> list[dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM progress_milestones WHERE student_id=? ORDER BY created_at ASC", (sid,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_milestone_status(mid: int, completed: bool):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE progress_milestones SET completed=? WHERE id=?", (int(completed), mid))
    conn.commit()
    conn.close()
