# src/skill_gap_analysis.py
# CareerMitra AI – Skill Gap Analysis Engine
# Re-usable logic layer; pages import this instead of duplicating the logic.

from __future__ import annotations

PROFICIENCY_SCORES: dict[str, int] = {
    "Beginner":     25,
    "Intermediate": 50,
    "Advanced":     75,
    "Expert":       100,
}

# Required proficiency score per skill per domain
REQUIRED_PROFICIENCY: dict[str, dict[str, int]] = {
    "Technology & Engineering": {
        "Python": 75, "Java": 50, "Cloud Computing": 50, "DevOps": 50, "System Design": 75,
    },
    "Data Science & AI/ML": {
        "Python": 75, "Machine Learning": 75, "SQL": 75,
        "Statistical Analysis": 50, "Data Analysis": 75,
    },
    "Business & Management": {
        "Business Analysis": 75, "Project Management": 75, "Leadership": 50,
        "Financial Modeling": 50, "Negotiation": 50,
    },
    "Healthcare & Medicine": {
        "Research": 75, "Critical Thinking": 75,
        "Data Analysis": 25, "Technical Writing": 25,
    },
    "Creative Arts & Design": {
        "Storytelling": 75, "Presentation Skills": 50, "Technical Writing": 50,
    },
    "Finance & Accounting": {
        "Financial Modeling": 75, "Data Analysis": 75,
        "Critical Thinking": 50, "Technical Writing": 50,
    },
    "Education & Research": {
        "Research": 75, "Technical Writing": 75, "Statistical Analysis": 50,
    },
    "Sales & Marketing": {
        "Public Speaking": 75, "Negotiation": 50, "Data Analysis": 50,
    },
    "Operations & Logistics": {
        "Problem Solving": 75, "Project Management": 50, "Data Analysis": 50,
    },
    "Law & Policy": {
        "Research": 75, "Critical Thinking": 75,
        "Technical Writing": 75, "Public Speaking": 50,
    },
}


def compute_gap(
    current_skills: list[dict],
    domain: str,
) -> dict[str, dict]:
    """
    Compute the skill gap for a student targeting *domain*.

    Parameters
    ----------
    current_skills : list of dicts with ``skill_name`` and optionally ``proficiency``
    domain         : Target career domain

    Returns
    -------
    dict keyed by skill name, each value is::

        {
            "required": int,   # required proficiency score (0–100)
            "current":  int,   # student's current proficiency score (0–100)
            "gap":      int,   # gap = max(required - current, 0)
            "status":   str,   # "✅ Met" | "⚠️ Partial" | "❌ Missing"
        }
    """
    required_map = REQUIRED_PROFICIENCY.get(domain, {})
    current_map  = {
        s["skill_name"]: PROFICIENCY_SCORES.get(s.get("proficiency", "Beginner"), 25)
        for s in current_skills
    }

    results: dict[str, dict] = {}
    for skill, req_score in required_map.items():
        curr = current_map.get(skill, 0)
        gap  = max(req_score - curr, 0)
        if gap == 0:
            status = "✅ Met"
        elif curr > 0:
            status = "⚠️ Partial"
        else:
            status = "❌ Missing"
        results[skill] = {"required": req_score, "current": curr, "gap": gap, "status": status}

    return results


def readiness_score(gap_results: dict) -> int:
    """Return overall readiness as an integer percentage (0–100)."""
    if not gap_results:
        return 0
    met = sum(1 for g in gap_results.values() if g["gap"] == 0)
    return round((met / len(gap_results)) * 100)


def missing_skills(gap_results: dict) -> list[str]:
    """Return the list of skills that are entirely missing (current == 0)."""
    return [s for s, d in gap_results.items() if d["current"] == 0]


def partial_skills(gap_results: dict) -> list[str]:
    """Return the list of skills that are partially met."""
    return [s for s, d in gap_results.items() if d["current"] > 0 and d["gap"] > 0]


def available_domains() -> list[str]:
    """Return all domains for which gap analysis is available."""
    return list(REQUIRED_PROFICIENCY.keys())
