# modules/progress_dashboard.py
# CareerMitra AI – Progress Tracking Dashboard

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from config.settings import COLORS
from database.db_manager import (
    get_student_by_id, get_skills, get_interests, get_career_goal,
    get_latest_recommendation, get_milestones, update_milestone_status,
    get_chat_history, save_milestones
)


def render_progress_dashboard(student_id: int | None):
    """Render the Progress Dashboard."""
    st.markdown("## 📋 Progress Dashboard")

    if not student_id:
        st.warning("👤 Please complete your **Student Profile** first to view your progress dashboard.")
        return

    student = get_student_by_id(student_id)
    if not student:
        st.error("Student data not found.")
        return

    skills = get_skills(student_id)
    interests = get_interests(student_id)
    goal = get_career_goal(student_id)
    rec = get_latest_recommendation(student_id)
    milestones = get_milestones(student_id)
    chat_history = get_chat_history(student_id)

    st.markdown(f"### 👋 Welcome back, **{student['name']}**!")
    if goal and goal.get("target_role"):
        st.markdown(f"*You're on the path to becoming a **{goal['target_role']}***")

    # ── Profile completion score ───────────────────────────────────────────────
    completion = _compute_profile_completion(student, skills, interests, goal)
    _render_profile_completion(completion)

    st.markdown("---")

    # ── KPI row ───────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    total_milestones = len(milestones)
    completed_milestones = sum(1 for m in milestones if m.get("completed"))
    progress_pct = round((completed_milestones / total_milestones) * 100) if total_milestones > 0 else 0
    total_chats = len(chat_history)
    total_skills = len(skills)

    _kpi_card(col1, "🎯 Goal Progress", f"{progress_pct}%", f"{completed_milestones}/{total_milestones} milestones", COLORS["primary"])
    _kpi_card(col2, "🛠️ Skills Registered", str(total_skills), "across all categories", COLORS["accent"])
    _kpi_card(col3, "🤖 AI Sessions", str(total_chats // 2), "counselor interactions", COLORS["secondary"])
    _kpi_card(col4, "📊 Profile Complete", f"{completion['total']}%", "fill all sections", COLORS["success"])

    st.markdown("---")

    # ── Milestone tracker ─────────────────────────────────────────────────────
    col_left, col_right = st.columns([3, 2])
    with col_left:
        _render_milestone_tracker(student_id, milestones)

    with col_right:
        _render_skill_breakdown_chart(skills)

    st.markdown("---")

    # ── Activity timeline ─────────────────────────────────────────────────────
    _render_activity_summary(student, skills, goal, rec, chat_history)


def _compute_profile_completion(student: dict, skills: list, interests: list, goal) -> dict:
    sections = {
        "Basic Info": all([student.get("name"), student.get("email"), student.get("age"), student.get("city")]),
        "Education": all([student.get("education"), student.get("stream")]),
        "Skills": len(skills) >= 3,
        "Interests": len(interests) >= 2,
        "Career Goal": goal is not None,
    }
    completed = sum(1 for v in sections.values() if v)
    total_pct = round((completed / len(sections)) * 100)
    return {"sections": sections, "total": total_pct, "completed": completed, "max": len(sections)}


def _render_profile_completion(completion: dict):
    total = completion["total"]
    color = COLORS["success"] if total >= 80 else (COLORS["warning"] if total >= 50 else COLORS["danger"])
    st.markdown(f"""
<div style="background:#1E293B; border:1px solid #334155; border-radius:10px; padding:1rem;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
        <span style="color:#F1F5F9; font-weight:600;">Profile Completion</span>
        <span style="color:{color}; font-weight:bold; font-size:1.1rem;">{total}%</span>
    </div>
    <div style="background:#0F172A; border-radius:6px; height:12px; margin-bottom:0.75rem;">
        <div style="background:{color}; height:12px; border-radius:6px; width:{total}%; transition:width 0.3s;"></div>
    </div>
    <div style="display:flex; gap:1rem; flex-wrap:wrap;">
        {"".join(f'<span style="color:{"#10B981" if v else "#EF4444"}; font-size:0.8rem;">{"✅" if v else "❌"} {k}</span>' for k, v in completion["sections"].items())}
    </div>
</div>
""", unsafe_allow_html=True)


def _render_milestone_tracker(student_id: int, milestones: list[dict]):
    st.markdown("### 📌 Learning Milestones")

    if not milestones:
        st.info("No milestones yet. Complete **Skill Gap Analysis** to auto-generate milestones, or add them below.")
        _add_custom_milestone(student_id)
        return

    # Sort: incomplete first
    milestones_sorted = sorted(milestones, key=lambda m: m.get("completed", 0))

    for m in milestones_sorted:
        col_check, col_title, col_cat = st.columns([0.5, 4, 2])
        with col_check:
            done = st.checkbox("", value=bool(m.get("completed")), key=f"ms_{m['id']}")
            if done != bool(m.get("completed")):
                update_milestone_status(m["id"], done)
                st.rerun()
        with col_title:
            style = "text-decoration:line-through; color:#94A3B8;" if m.get("completed") else "color:#F1F5F9;"
            st.markdown(f"<span style='{style}'>{m['title']}</span>", unsafe_allow_html=True)
        with col_cat:
            st.markdown(f"<span style='color:#7C3AED; font-size:0.75rem;'>{m.get('category','')}</span>", unsafe_allow_html=True)

    # Completion bar
    total = len(milestones)
    done = sum(1 for m in milestones if m.get("completed"))
    pct = round(done / total * 100) if total > 0 else 0
    st.markdown(f"""
<div style="margin-top:1rem; background:#0F172A; border-radius:6px; height:10px;">
    <div style="background:{COLORS['success']}; height:10px; border-radius:6px; width:{pct}%;"></div>
</div>
<div style="color:#94A3B8; font-size:0.8rem; margin-top:0.3rem;">{done}/{total} completed ({pct}%)</div>
""", unsafe_allow_html=True)

    st.markdown("")
    _add_custom_milestone(student_id, existing=milestones)


def _add_custom_milestone(student_id: int, existing: list = None):
    with st.expander("➕ Add Custom Milestone"):
        with st.form("add_milestone_form"):
            title = st.text_input("Milestone Title:")
            category = st.selectbox("Category:", ["Skill Development", "Certification", "Project", "Networking", "Application", "Other"])
            due_date = st.date_input("Due Date (optional):", value=None)
            submitted = st.form_submit_button("Add Milestone")
            if submitted and title:
                new_milestone = {"title": title, "category": category, "completed": False, "due_date": str(due_date) if due_date else None}
                all_milestones = (existing or []) + [new_milestone]
                # Re-save without IDs (save_milestones will recreate)
                clean = [{"title": m["title"], "category": m.get("category"), "completed": bool(m.get("completed")), "due_date": m.get("due_date")} for m in all_milestones]
                save_milestones(student_id, clean)
                st.success(f"✅ Milestone added: {title}")
                st.rerun()


def _render_skill_breakdown_chart(skills: list[dict]):
    st.markdown("### 🛠️ Skill Portfolio")
    if not skills:
        st.info("No skills registered yet. Add skills in your **Student Profile**.")
        return

    # Category donut
    from collections import Counter
    category_counts = Counter(s.get("category", "Other") for s in skills)
    fig = go.Figure(go.Pie(
        labels=list(category_counts.keys()), values=list(category_counts.values()),
        hole=0.55,
        marker_colors=[COLORS["primary"], COLORS["secondary"], COLORS["accent"], COLORS["success"]],
    ))
    fig.update_layout(
        paper_bgcolor="#0F172A", font_color="#F1F5F9",
        legend=dict(bgcolor="#1E293B", bordercolor="#334155", orientation="h"),
        height=280, margin=dict(l=5, r=5, t=5, b=5),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Proficiency breakdown
    prof_map = {"Expert": 4, "Advanced": 3, "Intermediate": 2, "Beginner": 1}
    prof_counts = Counter(s.get("proficiency", "Beginner") for s in skills)
    levels = ["Beginner", "Intermediate", "Advanced", "Expert"]
    counts = [prof_counts.get(l, 0) for l in levels]
    level_colors = [COLORS["danger"], COLORS["warning"], COLORS["accent"], COLORS["success"]]
    fig2 = go.Figure(go.Bar(x=levels, y=counts, marker_color=level_colors, text=counts, textposition="auto"))
    fig2.update_layout(
        plot_bgcolor="#0F172A", paper_bgcolor="#0F172A", font_color="#F1F5F9",
        height=220, margin=dict(l=5, r=5, t=5, b=5),
        yaxis=dict(gridcolor="#334155"), xaxis=dict(gridcolor="#334155"),
        title=dict(text="Proficiency Levels", font_color="#F1F5F9"),
    )
    st.plotly_chart(fig2, use_container_width=True)


def _render_activity_summary(student, skills, goal, rec, chat_history):
    st.markdown("### 📝 Profile Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
<div style="background:#1E293B; border:1px solid #334155; border-radius:10px; padding:1rem;">
    <h4 style="color:#06B6D4; margin-top:0;">👤 Student Info</h4>
    <table style="width:100%; color:#F1F5F9; font-size:0.9rem; border-collapse:collapse;">
        <tr><td style="color:#94A3B8; padding:3px 0;">Name</td><td>{student.get('name','—')}</td></tr>
        <tr><td style="color:#94A3B8; padding:3px 0;">Education</td><td>{student.get('education','—')}</td></tr>
        <tr><td style="color:#94A3B8; padding:3px 0;">Stream</td><td>{student.get('stream','—')}</td></tr>
        <tr><td style="color:#94A3B8; padding:3px 0;">City</td><td>{student.get('city','—')}</td></tr>
        <tr><td style="color:#94A3B8; padding:3px 0;">GPA</td><td>{student.get('gpa','—')}</td></tr>
    </table>
</div>
""", unsafe_allow_html=True)
    with col2:
        top_domain = rec.get("career_domain", "Not set") if rec else "Not set"
        top_role = goal.get("target_role", "Not set") if goal else "Not set"
        match_score = f"{rec.get('match_score', 0)}%" if rec else "—"
        st.markdown(f"""
<div style="background:#1E293B; border:1px solid #334155; border-radius:10px; padding:1rem;">
    <h4 style="color:#10B981; margin-top:0;">🎯 Career Snapshot</h4>
    <table style="width:100%; color:#F1F5F9; font-size:0.9rem; border-collapse:collapse;">
        <tr><td style="color:#94A3B8; padding:3px 0;">Top Domain</td><td>{top_domain}</td></tr>
        <tr><td style="color:#94A3B8; padding:3px 0;">Target Role</td><td>{top_role}</td></tr>
        <tr><td style="color:#94A3B8; padding:3px 0;">Match Score</td><td>{match_score}</td></tr>
        <tr><td style="color:#94A3B8; padding:3px 0;">Skills Count</td><td>{len(skills)}</td></tr>
        <tr><td style="color:#94A3B8; padding:3px 0;">AI Chats</td><td>{len(chat_history) // 2} sessions</td></tr>
    </table>
</div>
""", unsafe_allow_html=True)


def _kpi_card(col, title: str, value: str, subtitle: str, color: str):
    with col:
        st.markdown(f"""
<div style="background:#1E293B; border:1px solid #334155; border-left:4px solid {color}; border-radius:8px; padding:1rem; text-align:center; margin-bottom:1rem;">
    <div style="color:#94A3B8; font-size:0.8rem;">{title}</div>
    <div style="color:{color}; font-size:1.8rem; font-weight:bold;">{value}</div>
    <div style="color:#94A3B8; font-size:0.75rem;">{subtitle}</div>
</div>
""", unsafe_allow_html=True)
