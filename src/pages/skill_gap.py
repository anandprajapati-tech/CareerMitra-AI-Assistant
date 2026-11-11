# src/pages/skill_gap.py
# CareerMitra AI – Skill Gap Analysis Page (IBM Granite enhanced)

import streamlit as st
import plotly.graph_objects as go
from src.config import COLORS
from src.database import (
    get_student_by_id, get_skills, get_career_goal,
    get_latest_recommendation, save_milestones,
)
from src.ibm_granite import granite_skill_gap_analysis
import json, os


def _load_career_data() -> dict:
    path = os.path.join("data", "career_data.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


PROFICIENCY_SCORES = {"Beginner": 25, "Intermediate": 50, "Advanced": 75, "Expert": 100}

REQUIRED_PROFICIENCY = {
    "Technology & Engineering": {"Python": 75, "Java": 50, "Cloud Computing": 50, "DevOps": 50, "System Design": 75},
    "Data Science & AI/ML":     {"Python": 75, "Machine Learning": 75, "SQL": 75, "Statistical Analysis": 50, "Data Analysis": 75},
    "Business & Management":    {"Business Analysis": 75, "Project Management": 75, "Leadership": 50, "Financial Modeling": 50, "Negotiation": 50},
    "Healthcare & Medicine":    {"Research": 75, "Critical Thinking": 75, "Data Analysis": 25, "Technical Writing": 25},
    "Creative Arts & Design":   {"Storytelling": 75, "Presentation Skills": 50, "Technical Writing": 50},
    "Finance & Accounting":     {"Financial Modeling": 75, "Data Analysis": 75, "Critical Thinking": 50, "Technical Writing": 50},
    "Education & Research":     {"Research": 75, "Technical Writing": 75, "Statistical Analysis": 50},
    "Sales & Marketing":        {"Public Speaking": 75, "Negotiation": 50, "Data Analysis": 50},
}


def _compute_gap(current_skills: list[dict], required: dict) -> dict:
    current_map = {s["skill_name"]: PROFICIENCY_SCORES.get(s.get("proficiency","Beginner"), 25)
                   for s in current_skills}
    results = {}
    for skill, req_score in required.items():
        curr = current_map.get(skill, 0)
        gap = max(req_score - curr, 0)
        results[skill] = {
            "required": req_score, "current": curr, "gap": gap,
            "status": "✅ Met" if gap == 0 else ("⚠️ Partial" if curr > 0 else "❌ Missing"),
        }
    return results


def render_skill_gap_analysis(student_id: int | None):
    st.markdown("## 📊 Skill Gap Analysis")
    st.markdown("Compare your current skills against what your target career requires — enhanced by IBM Granite.")

    if not student_id:
        st.warning("👤 Complete your **Student Profile** first.")
        return

    skills = get_skills(student_id)
    rec    = get_latest_recommendation(student_id)
    goal   = get_career_goal(student_id)
    career_data = _load_career_data()

    available = list(REQUIRED_PROFICIENCY.keys())
    default_domain = None
    if goal and goal.get("goal_domain") in available:
        default_domain = goal["goal_domain"]
    elif rec and rec.get("career_domain") in available:
        default_domain = rec["career_domain"]

    selected = st.selectbox("🎯 Target Career Domain:",
                             available,
                             index=available.index(default_domain) if default_domain else 0)

    required = REQUIRED_PROFICIENCY.get(selected, {})
    gap_results = _compute_gap(skills, required)

    total     = len(gap_results)
    met       = sum(1 for g in gap_results.values() if g["gap"] == 0)
    partial   = sum(1 for g in gap_results.values() if 0 < g["gap"] < g["required"])
    missing   = sum(1 for g in gap_results.values() if g["current"] == 0)
    readiness = round((met / total) * 100) if total else 0

    # KPIs
    cols = st.columns(4)
    for col, (title, val, sub, color) in zip(cols, [
        ("🎯 Readiness",      f"{readiness}%",  "overall",           COLORS["primary"]),
        ("✅ Skills Met",     str(met),          f"of {total}",       COLORS["success"]),
        ("⚠️ Partial",        str(partial),      "need improvement",  COLORS["warning"]),
        ("❌ Missing",        str(missing),      "to acquire",        COLORS["danger"]),
    ]):
        with col:
            st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-left:4px solid {color};
            border-radius:8px;padding:1rem;text-align:center;">
    <div style="color:#94A3B8;font-size:0.78rem;">{title}</div>
    <div style="color:{color};font-size:1.8rem;font-weight:bold;">{val}</div>
    <div style="color:#94A3B8;font-size:0.72rem;">{sub}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")
    _radar(gap_results)

    st.markdown("### 🔍 Skill Breakdown")
    for skill, data in gap_results.items():
        _progress_bar(skill, data)

    # IBM Granite AI analysis
    st.markdown("---")
    st.markdown("### 🤖 IBM Granite AI Analysis")
    if st.button("Get AI-Powered Gap Analysis", use_container_width=True):
        with st.spinner("IBM Granite is analysing your skill gap..."):
            current_skill_names = [s["skill_name"] for s in skills]
            required_skill_names = list(required.keys())
            ai_text = granite_skill_gap_analysis(selected, current_skill_names, required_skill_names)
        st.markdown(ai_text)

    # Learning resources
    st.markdown("---")
    st.markdown("### 📚 Learning Resources")
    resources = career_data.get("learning_resources", {})
    gap_skills = [s for s, d in gap_results.items() if d["gap"] > 0]
    if gap_skills:
        for skill in gap_skills[:5]:
            res = resources.get(skill, [])
            with st.expander(f"📖 Learn **{skill}**"):
                if res:
                    for r in res:
                        st.markdown(f"• {r}")
                else:
                    st.markdown(f"• Search: *'{skill} course Coursera'* or *'{skill} tutorial YouTube'*")
    else:
        st.success("🎉 You have all required skills! Deepen your expertise.")

    if gap_skills and st.button("📋 Auto-generate Milestones from Gaps", use_container_width=True):
        milestones = [{"title": f"Learn {s}", "category": "Skill Development",
                       "completed": False, "due_date": None} for s in gap_skills[:8]]
        save_milestones(student_id, milestones)
        st.success(f"✅ {len(milestones)} milestones saved to Progress Dashboard!")


def _radar(gap_results: dict):
    skills = list(gap_results.keys())
    curr   = [gap_results[s]["current"] for s in skills]
    req    = [gap_results[s]["required"] for s in skills]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=req+[req[0]], theta=skills+[skills[0]],
        fill="toself", name="Required", line_color="#EF4444", fillcolor="rgba(239,68,68,0.15)"))
    fig.add_trace(go.Scatterpolar(r=curr+[curr[0]], theta=skills+[skills[0]],
        fill="toself", name="Current", line_color="#4F46E5", fillcolor="rgba(79,70,229,0.25)"))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,110], gridcolor="#334155"), bgcolor="#1E293B"),
        paper_bgcolor="#0F172A", font_color="#F1F5F9",
        legend=dict(bgcolor="#1E293B", bordercolor="#334155"),
        height=420, margin=dict(t=20, b=20),
        title=dict(text="Skill Radar: Current vs Required", font_color="#F1F5F9"),
    )
    st.plotly_chart(fig, use_container_width=True)


def _progress_bar(skill: str, data: dict):
    sc = {"✅ Met": "#10B981", "⚠️ Partial": "#F59E0B", "❌ Missing": "#EF4444"}
    color = sc.get(data["status"], "#94A3B8")
    st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:8px;
            padding:0.75rem 1rem;margin-bottom:0.4rem;">
    <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
        <span style="color:#F1F5F9;font-weight:600;">{skill}</span>
        <span style="color:{color};font-size:0.82rem;">{data['status']}</span>
    </div>
    <div style="background:#0F172A;border-radius:4px;height:8px;">
        <div style="background:#4F46E5;height:8px;border-radius:4px;width:{data['current']}%;"></div>
    </div>
    <div style="display:flex;justify-content:space-between;color:#94A3B8;font-size:0.72rem;margin-top:0.2rem;">
        <span>Current: {data['current']}%</span><span>Required: {data['required']}%</span>
    </div>
</div>""", unsafe_allow_html=True)
