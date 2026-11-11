# src/career_recommendation.py
# CareerMitra AI – Career Recommendation Engine
# Thin facade over the page-level scoring logic; re-usable from tests / CLI.

from __future__ import annotations

DOMAIN_STREAM_MAP: dict[str, list[str]] = {
    "Technology & Engineering":  ["Science (PCM)", "Engineering", "Computer Science"],
    "Data Science & AI/ML":      ["Science (PCM)", "Engineering", "Computer Science"],
    "Business & Management":     ["Commerce", "Arts / Humanities"],
    "Healthcare & Medicine":     ["Science (PCB)", "Medical"],
    "Creative Arts & Design":    ["Arts / Humanities"],
    "Education & Research":      ["Arts / Humanities", "Science (PCB)", "Science (PCM)"],
    "Finance & Accounting":      ["Commerce", "Engineering"],
    "Sales & Marketing":         ["Commerce", "Arts / Humanities"],
    "Operations & Logistics":    ["Engineering", "Commerce"],
    "Law & Policy":              ["Arts / Humanities"],
}

DOMAIN_INTEREST_MAP: dict[str, list[str]] = {
    "Technology & Engineering":  ["programming & coding", "mathematics & statistics"],
    "Data Science & AI/ML":      ["programming & coding", "mathematics & statistics"],
    "Business & Management":     ["business & entrepreneurship", "finance & investment"],
    "Healthcare & Medicine":     ["healthcare & wellness", "biology & life sciences"],
    "Creative Arts & Design":    ["art & design", "music & performing arts"],
    "Education & Research":      ["teaching & mentoring", "writing & literature"],
    "Finance & Accounting":      ["finance & investment", "mathematics & statistics"],
    "Sales & Marketing":         ["business & entrepreneurship", "writing & literature"],
    "Operations & Logistics":    ["business & entrepreneurship", "mathematics & statistics"],
    "Law & Policy":              ["social work & ngos", "government & politics"],
}

REQUIRED_SKILLS: dict[str, list[str]] = {
    "Technology & Engineering":  ["Python", "Java", "Cloud Computing", "DevOps", "System Design"],
    "Data Science & AI/ML":      ["Python", "Machine Learning", "SQL", "Statistical Analysis", "Data Analysis"],
    "Business & Management":     ["Business Analysis", "Leadership", "Financial Modeling", "Project Management"],
    "Healthcare & Medicine":     ["Research", "Critical Thinking", "Data Analysis"],
    "Creative Arts & Design":    ["Storytelling", "Presentation Skills", "Technical Writing"],
    "Finance & Accounting":      ["Financial Modeling", "Data Analysis", "Critical Thinking", "Technical Writing"],
    "Education & Research":      ["Research", "Technical Writing", "Statistical Analysis"],
    "Sales & Marketing":         ["Public Speaking", "Negotiation", "Data Analysis"],
    "Operations & Logistics":    ["Problem Solving", "Project Management", "Data Analysis"],
    "Law & Policy":              ["Research", "Critical Thinking", "Technical Writing", "Public Speaking"],
}


def score_domain(
    domain: str,
    skills: list[dict],
    interests: list[str],
    stream: str,
) -> float:
    """
    Score a career domain (0–100) for a student.

    Parameters
    ----------
    domain    : Career domain name (key in REQUIRED_SKILLS)
    skills    : List of dicts with at minimum ``{"skill_name": str}``
    interests : List of interest strings
    stream    : Academic stream string
    """
    skill_names     = {s["skill_name"].lower() for s in skills}
    interest_lower  = {i.lower() for i in interests}
    required        = [s.lower() for s in REQUIRED_SKILLS.get(domain, [])]

    # Up to 45 pts for matching required skills
    skill_score = min(len(skill_names & set(required)) * 15, 45)

    # Up to 35 pts for matching interests
    relevant_interests = {i.lower() for i in DOMAIN_INTEREST_MAP.get(domain, [])}
    interest_score = min(len(interest_lower & relevant_interests) * 20, 35)

    # 20 pts for stream alignment
    stream_score = 20 if stream and stream in DOMAIN_STREAM_MAP.get(domain, []) else 0

    return round(min(skill_score + interest_score + stream_score, 100), 1)


def rank_domains(
    skills: list[dict],
    interests: list[str],
    stream: str,
) -> list[tuple[str, float]]:
    """
    Return all career domains ranked by score (highest first).
    """
    scores = {d: score_domain(d, skills, interests, stream) for d in REQUIRED_SKILLS}
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def get_top_recommendations(
    skills: list[dict],
    interests: list[str],
    stream: str,
    top_n: int = 3,
) -> list[dict]:
    """
    Return the top-N career recommendations as structured dicts.
    Each dict has keys: domain, score, required_skills, missing_skills.
    """
    ranked = rank_domains(skills, interests, stream)[:top_n]
    skill_names = {s["skill_name"] for s in skills}
    result = []
    for domain, score in ranked:
        req = REQUIRED_SKILLS.get(domain, [])
        missing = [s for s in req if s not in skill_names]
        result.append({
            "domain":          domain,
            "score":           score,
            "required_skills": req,
            "missing_skills":  missing,
        })
    return result
