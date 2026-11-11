# src/progress_tracking.py
# CareerMitra AI – Progress Tracking Helpers
# Business-logic layer for milestone management and progress reporting.

from __future__ import annotations
from src.database import (
    get_milestones, save_milestones, update_milestone_status,
    get_skills, get_interests, get_career_goal, get_student_by_id,
    get_latest_recommendation, get_chat_history,
)


# ── Profile completion ────────────────────────────────────────────────────────

def profile_completion(student_id: int) -> dict:
    """
    Return a completion summary dict for the student's profile.

    Returns
    -------
    {
        "pct":    int,           # overall completion 0–100
        "done":   int,           # sections completed
        "total":  int,           # total sections
        "checks": dict[str, bool]
    }
    """
    student   = get_student_by_id(student_id)
    skills    = get_skills(student_id)
    interests = get_interests(student_id)
    goal      = get_career_goal(student_id)

    checks = {
        "Basic Info":     bool(student and student.get("name") and student.get("email")),
        "Education":      bool(student and student.get("education")),
        "Skills (3+)":    len(skills) >= 3,
        "Interests (2+)": len(interests) >= 2,
        "Career Goal":    goal is not None,
    }
    done = sum(checks.values())
    return {
        "checks": checks,
        "pct":    round(done / len(checks) * 100),
        "done":   done,
        "total":  len(checks),
    }


# ── Milestones ────────────────────────────────────────────────────────────────

def milestone_progress(student_id: int) -> dict:
    """
    Return milestone progress statistics for the student.

    Returns
    -------
    {
        "total":     int,
        "completed": int,
        "pending":   int,
        "pct":       int,   # 0–100
        "milestones": list[dict]
    }
    """
    milestones = get_milestones(student_id)
    completed  = sum(1 for m in milestones if m.get("completed"))
    total      = len(milestones)
    return {
        "total":      total,
        "completed":  completed,
        "pending":    total - completed,
        "pct":        round((completed / total) * 100) if total else 0,
        "milestones": milestones,
    }


def add_milestone(student_id: int, title: str, category: str = "Skill Development",
                  due_date: str | None = None) -> list[dict]:
    """
    Append a new milestone for the student and return the updated list.
    """
    existing = get_milestones(student_id)
    new_entry = {"title": title, "category": category, "completed": False, "due_date": due_date}
    all_ms = existing + [new_entry]
    # Re-save the whole list (save_milestones replaces all rows)
    clean = [
        {
            "title":    m["title"],
            "category": m.get("category"),
            "completed": bool(m.get("completed")),
            "due_date": m.get("due_date"),
        }
        for m in all_ms
    ]
    save_milestones(student_id, clean)
    return get_milestones(student_id)


def auto_generate_milestones_from_gaps(student_id: int, gap_skills: list[str]) -> int:
    """
    Auto-generate milestones from the list of missing/partial skills.
    Replaces all existing milestones.
    Returns the count of milestones created.
    """
    milestones = [
        {"title": f"Learn {skill}", "category": "Skill Development",
         "completed": False, "due_date": None}
        for skill in gap_skills[:10]
    ]
    save_milestones(student_id, milestones)
    return len(milestones)


def mark_milestone(milestone_id: int, completed: bool) -> None:
    """Toggle a milestone's completed state."""
    update_milestone_status(milestone_id, completed)


# ── Dashboard summary ─────────────────────────────────────────────────────────

def full_summary(student_id: int) -> dict:
    """
    Return a comprehensive summary dict used by the Progress Dashboard.

    Keys: student, skills, interests, goal, rec, milestones_stats, ai_sessions,
          profile_completion.
    """
    student    = get_student_by_id(student_id)
    skills     = get_skills(student_id)
    interests  = get_interests(student_id)
    goal       = get_career_goal(student_id)
    rec        = get_latest_recommendation(student_id)
    chat       = get_chat_history(student_id)
    ms_stats   = milestone_progress(student_id)
    completion = profile_completion(student_id)

    return {
        "student":             student,
        "skills":              skills,
        "interests":           interests,
        "goal":                goal,
        "recommendation":      rec,
        "milestones_stats":    ms_stats,
        "ai_sessions":         len(chat) // 2,
        "profile_completion":  completion,
    }
