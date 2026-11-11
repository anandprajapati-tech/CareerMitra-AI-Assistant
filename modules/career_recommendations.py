# modules/career_recommendations.py
# CareerMitra AI – Career Recommendations Engine

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import json
import os
from config.settings import CAREER_DOMAINS, COLORS
from database.db_manager import (
    get_student_by_id, get_skills, get_interests,
    get_career_goal, save_recommendation, get_latest_recommendation
)


def _load_career_data() -> dict:
    path = os.path.join("data", "career_data.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def _score_career(domain: str, data: dict, skills: list[dict], interests: list[str], stream: str) -> float:
    """Compute a match score (0–100) for a career domain."""
    score = 0.0
    skill_names = {s["skill_name"].lower() for s in skills}
    interest_lower = {i.lower() for i in interests}

    top_skills = [s.lower() for s in data.get("top_skills", [])]
    skill_overlap = len(skill_names & set(top_skills))
    score += min(skill_overlap * 12, 40)   # max 40 pts from skills

    domain_interest_map = {
        "Technology & Engineering": ["programming & coding", "mathematics & statistics"],
        "Data Science & AI/ML": ["programming & coding", "mathematics & statistics"],
        "Business & Management": ["business & entrepreneurship", "finance & investment"],
        "Healthcare & Medicine": ["healthcare & wellness", "biology & life sciences"],
        "Creative Arts & Design": ["art & design", "music & performing arts"],
        "Education & Research": ["teaching & mentoring", "writing & literature"],
        "Finance & Accounting": ["finance & investment", "mathematics & statistics"],
        "Sales & Marketing": ["business & entrepreneurship", "writing & literature"],
    }
    relevant_interests = {i.lower() for i in domain_interest_map.get(domain, [])}
    interest_overlap = len(interest_lower & relevant_interests)
    score += min(interest_overlap * 20, 40)   # max 40 pts from interests

    stream_career_map = {
        "Science (PCM)": ["Technology & Engineering", "Data Science & AI/ML", "Finance & Accounting"],
        "Science (PCB)": ["Healthcare & Medicine", "Education & Research"],
        "Commerce": ["Business & Management", "Finance & Accounting", "Sales & Marketing"],
        "Arts / Humanities": ["Education & Research", "Creative Arts & Design", "Sales & Marketing"],
        "Engineering": ["Technology & Engineering", "Data Science & AI/ML"],
        "Computer Science": ["Technology & Engineering", "Data Science & AI/ML"],
        "Medical": ["Healthcare & Medicine"],
    }
    if stream and domain in stream_career_map.get(stream, []):
        score += 20   # 20 pts from stream alignment

    return round(min(score, 100), 1)


def render_career_recommendations(student_id: int | None):
    """Render the Career Recommendations page."""
    st.markdown("## 🎯 Career Recommendations")

    if not student_id:
        st.warning("👤 Please complete your **Student Profile** first to get personalised career recommendations.")
        _render_generic_recommendations()
        return

    student = get_student_by_id(student_id)
    skills = get_skills(student_id)
    interests = get_interests(student_id)
    career_data = _load_career_data()

    if not student:
        st.error("Student data not found. Please re-save your profile.")
        return

    st.markdown(f"### 👋 Recommendations for **{student['name']}**")
    st.markdown(f"*Based on your education ({student.get('education', 'N/A')}), skills, and interests*")

    # ── Compute scores ────────────────────────────────────────────────────────
    scores = {}
    for domain, data in career_data.get("career_paths", {}).items():
        scores[domain] = _score_career(domain, data, skills, interests, student.get("stream", ""))

    sorted_domains = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # ── Save top recommendation ───────────────────────────────────────────────
    if sorted_domains:
        top_domain, top_score = sorted_domains[0]
        top_data = career_data["career_paths"].get(top_domain, {})
        save_recommendation(student_id, {
            "domain": top_domain,
            "roles": top_data.get("roles", []),
            "score": top_score,
            "reasoning": f"Best match based on skills and interests alignment ({top_score}%).",
        })

    # ── Top 3 career cards ────────────────────────────────────────────────────
    st.markdown("### 🏆 Your Top Career Matches")
    top3 = sorted_domains[:3]
    cols = st.columns(3)
    medals = ["🥇", "🥈", "🥉"]
    for idx, (domain, score) in enumerate(top3):
        data = career_data["career_paths"].get(domain, {})
        with cols[idx]:
            demand_color = {"Very High": "#10B981", "High": "#06B6D4", "Medium-High": "#F59E0B", "Medium": "#F59E0B", "Stable": "#94A3B8"}.get(data.get("demand_growth", ""), "#94A3B8")
            st.markdown(f"""
<div style="background:#1E293B; border:1px solid #334155; border-radius:12px; padding:1.2rem; text-align:center;">
    <div style="font-size:2rem;">{medals[idx]}</div>
    <h4 style="color:#F1F5F9; margin:0.5rem 0;">{domain}</h4>
    <div style="font-size:1.8rem; font-weight:bold; color:#4F46E5;">{score}%</div>
    <div style="color:#94A3B8; font-size:0.8rem;">Match Score</div>
    <div style="margin:0.5rem 0; padding:0.25rem 0.75rem; background:{demand_color}22; color:{demand_color}; border-radius:20px; font-size:0.8rem; display:inline-block;">
        📈 {data.get('demand_growth','N/A')} Demand
    </div>
    <div style="color:#94A3B8; font-size:0.8rem; margin-top:0.5rem;">
        Avg ₹{data.get('avg_salary_inr', 0)//100000}L/year
    </div>
</div>
""", unsafe_allow_html=True)

    # ── Score bar chart ───────────────────────────────────────────────────────
    st.markdown("### 📊 Full Career Match Analysis")
    domains_list = [d for d, _ in sorted_domains]
    scores_list = [s for _, s in sorted_domains]
    bar_colors = [COLORS["primary"] if i < 3 else COLORS["text_muted"] for i in range(len(domains_list))]

    fig = go.Figure(go.Bar(
        y=domains_list, x=scores_list, orientation="h",
        marker_color=bar_colors,
        text=[f"{s}%" for s in scores_list], textposition="outside",
    ))
    fig.update_layout(
        plot_bgcolor="#0F172A", paper_bgcolor="#0F172A",
        font_color="#F1F5F9", xaxis_title="Match Score (%)",
        xaxis=dict(range=[0, 110], gridcolor="#334155"),
        yaxis=dict(gridcolor="#334155"),
        height=380, margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Detailed view for top domain ──────────────────────────────────────────
    st.markdown("### 🔍 Deep Dive: Top Match")
    selected_domain = st.selectbox("Explore a career domain:", [d for d, _ in sorted_domains])
    _render_domain_details(selected_domain, career_data, scores.get(selected_domain, 0))


def _render_domain_details(domain: str, career_data: dict, score: float):
    data = career_data.get("career_paths", {}).get(domain, {})
    if not data:
        st.error("No data available for this domain.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
<div style="background:#1E293B; border:1px solid #334155; border-radius:10px; padding:1rem;">
    <h4 style="color:#06B6D4;">🎭 Key Roles</h4>
    {"".join(f'<div style="padding:0.25rem 0; color:#F1F5F9;">• {r}</div>' for r in data.get('roles', []))}
</div>
""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
<div style="background:#1E293B; border:1px solid #334155; border-radius:10px; padding:1rem;">
    <h4 style="color:#10B981;">🛠️ Top Skills Required</h4>
    {"".join(f'<div style="padding:0.25rem 0; color:#F1F5F9;">• {s}</div>' for s in data.get('top_skills', []))}
</div>
""", unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"""
<div style="background:#1E293B; border:1px solid #334155; border-radius:10px; padding:1rem; margin-top:1rem;">
    <h4 style="color:#F59E0B;">🏢 Top Companies</h4>
    {"".join(f'<div style="padding:0.25rem 0; color:#F1F5F9;">• {c}</div>' for c in data.get('top_companies', []))}
</div>
""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
<div style="background:#1E293B; border:1px solid #334155; border-radius:10px; padding:1rem; margin-top:1rem;">
    <h4 style="color:#7C3AED;">🎓 Education Pathways</h4>
    {"".join(f'<div style="padding:0.25rem 0; color:#F1F5F9;">• {e}</div>' for e in data.get('education', []))}
    <hr style="border-color:#334155; margin:0.75rem 0;">
    <div style="color:#10B981; font-weight:bold;">💰 Avg Salary: ₹{data.get('avg_salary_inr',0)//100000}L/year</div>
    <div style="color:#06B6D4; font-size:0.85rem;">📈 Demand: {data.get('demand_growth','N/A')}</div>
</div>
""", unsafe_allow_html=True)


def _render_generic_recommendations():
    st.markdown("---")
    st.markdown("### 🌐 Popular Career Domains in India (2025)")
    career_data = _load_career_data()
    for domain, data in list(career_data.get("career_paths", {}).items())[:4]:
        with st.expander(f"**{domain}** — Avg ₹{data.get('avg_salary_inr',0)//100000}L/year | Demand: {data.get('demand_growth','N/A')}"):
            st.markdown(f"**Roles:** {', '.join(data.get('roles', []))}")
            st.markdown(f"**Top Skills:** {', '.join(data.get('top_skills', []))}")
            st.markdown(f"**Education:** {', '.join(data.get('education', []))}")
