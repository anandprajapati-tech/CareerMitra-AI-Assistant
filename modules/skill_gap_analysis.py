# modules/skill_gap_analysis.py
# CareerMitra AI – Skill Gap Analysis Module

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import json
import os
from config.settings import SKILL_CATEGORIES, PROFICIENCY_LEVELS, COLORS
from database.db_manager import (
    get_student_by_id, get_skills, get_career_goal,
    get_latest_recommendation, save_milestones
)


def _load_career_data() -> dict:
    path = os.path.join("data", "career_data.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


PROFICIENCY_SCORES = {"Beginner": 25, "Intermediate": 50, "Advanced": 75, "Expert": 100}

REQUIRED_PROFICIENCY = {
    "Technology & Engineering": {"Python": 75, "Java": 50, "Cloud Computing": 50, "DevOps": 50, "System Design": 75},
    "Data Science & AI/ML": {"Python": 75, "Machine Learning": 75, "SQL": 75, "Statistics": 50, "Deep Learning": 50},
    "Business & Management": {"Business Analysis": 75, "Project Management": 75, "Leadership": 50, "Financial Modeling": 50, "Negotiation": 50},
    "Healthcare & Medicine": {"Clinical Knowledge": 75, "Research": 75, "Patient Care": 75, "Data Analysis": 25},
    "Creative Arts & Design": {"Figma": 75, "User Research": 50, "Adobe Suite": 75, "Storytelling": 50},
    "Finance & Accounting": {"Financial Modeling": 75, "Accounting": 75, "Risk Analysis": 50, "Excel": 75, "Taxation": 50},
    "Education & Research": {"Research": 75, "Teaching": 75, "Statistical Analysis": 50, "Technical Writing": 50},
    "Sales & Marketing": {"Digital Marketing": 75, "SEO/SEM": 50, "CRM": 50, "Data Analytics": 50, "Communication": 75},
}


def _compute_gap(current_skills: list[dict], required: dict) -> dict:
    """Compare current skills against required; return gap analysis."""
    current_map = {s["skill_name"]: PROFICIENCY_SCORES.get(s.get("proficiency", "Beginner"), 25) for s in current_skills}
    results = {}
    for skill, req_score in required.items():
        current_score = current_map.get(skill, 0)
        gap = max(req_score - current_score, 0)
        results[skill] = {
            "required": req_score,
            "current": current_score,
            "gap": gap,
            "status": "✅ Met" if gap == 0 else ("⚠️ Partial" if current_score > 0 else "❌ Missing"),
        }
    return results


def render_skill_gap_analysis(student_id: int | None):
    """Render the Skill Gap Analysis page."""
    st.markdown("## 📊 Skill Gap Analysis")
    st.markdown("Compare your current skills against what your target career actually requires.")

    if not student_id:
        st.warning("👤 Please complete your **Student Profile** first to run skill gap analysis.")
        return

    student = get_student_by_id(student_id)
    current_skills = get_skills(student_id)
    career_data = _load_career_data()
    rec = get_latest_recommendation(student_id)
    goal = get_career_goal(student_id)

    # ── Domain selector ───────────────────────────────────────────────────────
    default_domain = None
    if goal and goal.get("goal_domain"):
        default_domain = goal["goal_domain"]
    elif rec and rec.get("career_domain"):
        default_domain = rec["career_domain"]

    available_domains = list(REQUIRED_PROFICIENCY.keys())
    default_idx = available_domains.index(default_domain) if default_domain in available_domains else 0

    selected_domain = st.selectbox(
        "🎯 Select Target Career Domain:",
        available_domains,
        index=default_idx,
        help="Choose the career you're aiming for to see your skill gaps."
    )

    required = REQUIRED_PROFICIENCY.get(selected_domain, {})
    gap_results = _compute_gap(current_skills, required)

    # ── Summary KPIs ──────────────────────────────────────────────────────────
    total = len(gap_results)
    met = sum(1 for g in gap_results.values() if g["gap"] == 0)
    partial = sum(1 for g in gap_results.values() if 0 < g["gap"] < g["required"])
    missing = sum(1 for g in gap_results.values() if g["current"] == 0)
    readiness = round((met / total) * 100) if total > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    _metric_card(col1, "🎯 Career Readiness", f"{readiness}%", "Overall match", COLORS["primary"])
    _metric_card(col2, "✅ Skills Met", str(met), f"of {total} required", COLORS["success"])
    _metric_card(col3, "⚠️ Partial Skills", str(partial), "need improvement", COLORS["warning"])
    _metric_card(col4, "❌ Skills Missing", str(missing), "to acquire", COLORS["danger"])

    st.markdown("---")

    # ── Radar chart ───────────────────────────────────────────────────────────
    _render_radar_chart(gap_results)

    # ── Skill-by-skill breakdown ───────────────────────────────────────────────
    st.markdown("### 🔍 Skill-by-Skill Breakdown")
    for skill, data in gap_results.items():
        _render_skill_progress_bar(skill, data)

    # ── Learning resources for gaps ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📚 Recommended Learning Resources")
    learning_resources = career_data.get("learning_resources", {})
    gap_skills = [skill for skill, data in gap_results.items() if data["gap"] > 0]

    if gap_skills:
        for skill in gap_skills[:5]:
            resources = learning_resources.get(skill, [])
            if resources:
                with st.expander(f"📖 Resources to learn **{skill}**"):
                    for r in resources:
                        st.markdown(f"• {r}")
            else:
                with st.expander(f"📖 Resources to learn **{skill}**"):
                    st.markdown(f"• Search: *'{skill} course Coursera'* or *'{skill} tutorial YouTube'*")
    else:
        st.success("🎉 You have all the skills required for this career domain! Consider deepening your expertise.")

    # ── Auto-generate learning milestones ────────────────────────────────────
    if gap_skills and st.button("📋 Generate Learning Milestones", use_container_width=True):
        milestones = []
        for i, skill in enumerate(gap_skills[:8]):
            milestones.append({
                "title": f"Learn {skill}",
                "category": "Skill Development",
                "completed": False,
                "due_date": None,
            })
        save_milestones(student_id, milestones)
        st.success(f"✅ {len(milestones)} learning milestones saved to your Progress Dashboard!")


def _render_radar_chart(gap_results: dict):
    skills = list(gap_results.keys())
    current_vals = [gap_results[s]["current"] for s in skills]
    required_vals = [gap_results[s]["required"] for s in skills]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=required_vals + [required_vals[0]], theta=skills + [skills[0]],
        fill="toself", name="Required", line_color="#EF4444", fillcolor="rgba(239,68,68,0.15)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=current_vals + [current_vals[0]], theta=skills + [skills[0]],
        fill="toself", name="Your Level", line_color="#4F46E5", fillcolor="rgba(79,70,229,0.25)",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 110], gridcolor="#334155"), bgcolor="#1E293B"),
        paper_bgcolor="#0F172A", font_color="#F1F5F9",
        legend=dict(bgcolor="#1E293B", bordercolor="#334155"),
        height=420, margin=dict(t=20, b=20),
        title=dict(text="Skill Radar: Current vs Required", font_color="#F1F5F9"),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_skill_progress_bar(skill: str, data: dict):
    status_color = {"✅ Met": "#10B981", "⚠️ Partial": "#F59E0B", "❌ Missing": "#EF4444"}.get(data["status"], "#94A3B8")
    bar_fill = int((data["current"] / 100) * 100)
    req_fill = int((data["required"] / 100) * 100)
    st.markdown(f"""
<div style="background:#1E293B; border:1px solid #334155; border-radius:8px; padding:0.75rem 1rem; margin-bottom:0.5rem;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
        <span style="color:#F1F5F9; font-weight:600;">{skill}</span>
        <span style="color:{status_color}; font-size:0.85rem;">{data['status']}</span>
    </div>
    <div style="background:#0F172A; border-radius:4px; height:8px; position:relative;">
        <div style="background:#4F46E5; height:8px; border-radius:4px; width:{bar_fill}%;"></div>
    </div>
    <div style="display:flex; justify-content:space-between; color:#94A3B8; font-size:0.75rem; margin-top:0.2rem;">
        <span>Your level: {data['current']}%</span>
        <span>Required: {data['required']}%</span>
    </div>
</div>
""", unsafe_allow_html=True)


def _metric_card(col, title: str, value: str, subtitle: str, color: str):
    with col:
        st.markdown(f"""
<div style="background:#1E293B; border:1px solid #334155; border-left:4px solid {color}; border-radius:8px; padding:1rem; text-align:center;">
    <div style="color:#94A3B8; font-size:0.8rem;">{title}</div>
    <div style="color:{color}; font-size:1.8rem; font-weight:bold;">{value}</div>
    <div style="color:#94A3B8; font-size:0.75rem;">{subtitle}</div>
</div>
""", unsafe_allow_html=True)
