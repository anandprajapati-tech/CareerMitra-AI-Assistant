# src/pages/dashboard.py
# CareerMitra AI – Progress Dashboard Page

import streamlit as st
import plotly.graph_objects as go
from collections import Counter
from src.config import COLORS
from src.database import (
    get_student_by_id, get_skills, get_interests, get_career_goal,
    get_latest_recommendation, get_milestones, update_milestone_status,
    get_chat_history, save_milestones,
)


def render_dashboard(student_id: int | None):
    st.markdown("## 📋 Progress Dashboard")

    if not student_id:
        st.warning("👤 Complete your **Student Profile** to view your dashboard.")
        return

    student  = get_student_by_id(student_id)
    if not student:
        st.error("Student record not found.")
        return

    skills       = get_skills(student_id)
    interests    = get_interests(student_id)
    goal         = get_career_goal(student_id)
    rec          = get_latest_recommendation(student_id)
    milestones   = get_milestones(student_id)
    chat_history = get_chat_history(student_id)

    st.markdown(f"### 👋 Welcome back, **{student['name']}**!")
    if goal and goal.get("target_role"):
        st.markdown(f"*Tracking your journey to become a **{goal['target_role']}***")

    # Profile completion
    completion = _completion(student, skills, interests, goal)
    _completion_bar(completion)
    st.markdown("---")

    # KPIs
    total_ms   = len(milestones)
    done_ms    = sum(1 for m in milestones if m.get("completed"))
    progress   = round((done_ms / total_ms) * 100) if total_ms else 0
    chat_count = len(chat_history) // 2

    c1, c2, c3, c4 = st.columns(4)
    for col, (title, val, sub, color) in zip([c1, c2, c3, c4], [
        ("🎯 Goal Progress",    f"{progress}%",      f"{done_ms}/{total_ms} milestones", COLORS["primary"]),
        ("🛠️ Skills",           str(len(skills)),     "registered",                       COLORS["accent"]),
        ("🤖 AI Sessions",      str(chat_count),      "with IBM Granite",                 COLORS["secondary"]),
        ("📊 Profile",          f"{completion['pct']}%", "complete",                      COLORS["success"]),
    ]):
        with col:
            st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-left:4px solid {color};
            border-radius:8px;padding:1rem;text-align:center;margin-bottom:1rem;">
    <div style="color:#94A3B8;font-size:0.78rem;">{title}</div>
    <div style="color:{color};font-size:1.8rem;font-weight:bold;">{val}</div>
    <div style="color:#94A3B8;font-size:0.72rem;">{sub}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_left, col_right = st.columns([3, 2])
    with col_left:
        _milestone_tracker(student_id, milestones)
    with col_right:
        _skill_chart(skills)

    st.markdown("---")
    _summary_cards(student, skills, goal, rec, chat_history)


def _completion(student, skills, interests, goal) -> dict:
    checks = {
        "Basic Info":     bool(student and student.get("name") and student.get("email")),
        "Education":      bool(student and student.get("education")),
        "Skills (3+)":    len(skills) >= 3,
        "Interests (2+)": len(interests) >= 2,
        "Career Goal":    goal is not None,
    }
    done = sum(checks.values())
    return {"checks": checks, "pct": round(done / len(checks) * 100), "done": done, "total": len(checks)}


def _completion_bar(comp: dict):
    pct   = comp["pct"]
    color = COLORS["success"] if pct >= 80 else (COLORS["warning"] if pct >= 50 else COLORS["danger"])
    st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:10px;padding:1rem;">
  <div style="display:flex;justify-content:space-between;margin-bottom:0.4rem;">
    <span style="color:#F1F5F9;font-weight:600;">Profile Completion</span>
    <span style="color:{color};font-weight:bold;">{pct}%</span>
  </div>
  <div style="background:#0F172A;border-radius:6px;height:10px;margin-bottom:0.6rem;">
    <div style="background:{color};height:10px;border-radius:6px;width:{pct}%;"></div>
  </div>
  <div style="display:flex;gap:1rem;flex-wrap:wrap;">
    {"".join(f'<span style="color:{"#10B981" if v else "#94A3B8"};font-size:0.78rem;">{"✅" if v else "⬜"} {k}</span>' for k,v in comp["checks"].items())}
  </div>
</div>""", unsafe_allow_html=True)


def _milestone_tracker(student_id: int, milestones: list[dict]):
    st.markdown("### 📌 Learning Milestones")
    if not milestones:
        st.info("No milestones yet. Run **Skill Gap Analysis** to auto-generate them.")
        _add_milestone_form(student_id, [])
        return

    sorted_ms = sorted(milestones, key=lambda m: m.get("completed", 0))
    for m in sorted_ms:
        c1, c2, c3 = st.columns([0.5, 4, 2])
        with c1:
            done = st.checkbox("", value=bool(m.get("completed")), key=f"ms_{m['id']}")
            if done != bool(m.get("completed")):
                update_milestone_status(m["id"], done)
                st.rerun()
        with c2:
            style = "text-decoration:line-through;color:#94A3B8;" if m.get("completed") else "color:#F1F5F9;"
            st.markdown(f"<span style='{style}'>{m['title']}</span>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<span style='color:#7C3AED;font-size:0.72rem;'>{m.get('category','')}</span>",
                        unsafe_allow_html=True)

    done_count = sum(1 for m in milestones if m.get("completed"))
    pct = round(done_count / len(milestones) * 100) if milestones else 0
    st.markdown(f"""
<div style="margin-top:0.75rem;background:#0F172A;border-radius:6px;height:8px;">
    <div style="background:{COLORS['success']};height:8px;border-radius:6px;width:{pct}%;"></div>
</div>
<div style="color:#94A3B8;font-size:0.72rem;margin-top:0.2rem;">{done_count}/{len(milestones)} ({pct}%)</div>
""", unsafe_allow_html=True)
    st.markdown("")
    _add_milestone_form(student_id, milestones)


def _add_milestone_form(student_id: int, existing: list):
    with st.expander("➕ Add Milestone"):
        with st.form("add_ms"):
            title    = st.text_input("Title:")
            category = st.selectbox("Category:", ["Skill Development","Certification","Project","Networking","Application","Other"])
            due      = st.date_input("Due Date (optional):", value=None)
            if st.form_submit_button("Add") and title:
                new = {"title": title, "category": category, "completed": False,
                       "due_date": str(due) if due else None}
                all_ms = existing + [new]
                clean  = [{"title": m["title"], "category": m.get("category"),
                            "completed": bool(m.get("completed")), "due_date": m.get("due_date")}
                           for m in all_ms]
                save_milestones(student_id, clean)
                st.success("✅ Milestone added!")
                st.rerun()


def _skill_chart(skills: list[dict]):
    st.markdown("### 🛠️ Skill Portfolio")
    if not skills:
        st.info("No skills yet. Add them in **Student Profile**.")
        return
    cat_counts  = Counter(s.get("category","Other") for s in skills)
    fig = go.Figure(go.Pie(
        labels=list(cat_counts.keys()), values=list(cat_counts.values()), hole=0.5,
        marker_colors=[COLORS["primary"], COLORS["secondary"], COLORS["accent"], COLORS["success"]],
    ))
    fig.update_layout(paper_bgcolor="#0F172A", font_color="#F1F5F9", height=260,
                      legend=dict(bgcolor="#1E293B", orientation="h"),
                      margin=dict(l=5, r=5, t=5, b=5))
    st.plotly_chart(fig, use_container_width=True)

    prof_counts = Counter(s.get("proficiency","Beginner") for s in skills)
    levels  = ["Beginner","Intermediate","Advanced","Expert"]
    counts  = [prof_counts.get(l, 0) for l in levels]
    lcolors = [COLORS["danger"], COLORS["warning"], COLORS["accent"], COLORS["success"]]
    fig2 = go.Figure(go.Bar(x=levels, y=counts, marker_color=lcolors, text=counts, textposition="auto"))
    fig2.update_layout(plot_bgcolor="#0F172A", paper_bgcolor="#0F172A", font_color="#F1F5F9",
                       height=210, margin=dict(l=5, r=5, t=5, b=5),
                       yaxis=dict(gridcolor="#334155"), xaxis=dict(gridcolor="#334155"),
                       title=dict(text="Proficiency Levels", font_color="#F1F5F9"))
    st.plotly_chart(fig2, use_container_width=True)


def _summary_cards(student, skills, goal, rec, chat_history):
    st.markdown("### 📝 Summary")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:10px;padding:1rem;">
  <h4 style="color:#06B6D4;margin-top:0;">👤 Student</h4>
  <table style="width:100%;color:#F1F5F9;font-size:0.88rem;border-collapse:collapse;">
    <tr><td style="color:#94A3B8;padding:2px 0;">Name</td><td>{student.get('name','—')}</td></tr>
    <tr><td style="color:#94A3B8;padding:2px 0;">Education</td><td>{student.get('education','—')}</td></tr>
    <tr><td style="color:#94A3B8;padding:2px 0;">Stream</td><td>{student.get('stream','—')}</td></tr>
    <tr><td style="color:#94A3B8;padding:2px 0;">City</td><td>{student.get('city','—')}</td></tr>
    <tr><td style="color:#94A3B8;padding:2px 0;">GPA</td><td>{student.get('gpa','—')}</td></tr>
  </table>
</div>""", unsafe_allow_html=True)
    with c2:
        top_d    = rec.get("career_domain","Not set") if rec else "Not set"
        top_role = goal.get("target_role","Not set") if goal else "Not set"
        score    = f"{rec.get('match_score',0)}%" if rec else "—"
        st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:10px;padding:1rem;">
  <h4 style="color:#10B981;margin-top:0;">🎯 Career Snapshot</h4>
  <table style="width:100%;color:#F1F5F9;font-size:0.88rem;border-collapse:collapse;">
    <tr><td style="color:#94A3B8;padding:2px 0;">Top Domain</td><td>{top_d}</td></tr>
    <tr><td style="color:#94A3B8;padding:2px 0;">Target Role</td><td>{top_role}</td></tr>
    <tr><td style="color:#94A3B8;padding:2px 0;">Match Score</td><td>{score}</td></tr>
    <tr><td style="color:#94A3B8;padding:2px 0;">Skills Count</td><td>{len(skills)}</td></tr>
    <tr><td style="color:#94A3B8;padding:2px 0;">AI Chats</td><td>{len(chat_history)//2}</td></tr>
  </table>
</div>""", unsafe_allow_html=True)
