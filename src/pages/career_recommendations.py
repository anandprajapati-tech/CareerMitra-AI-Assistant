# src/pages/career_recommendations.py
# CareerMitra AI Assistant – Career Recommendations Page (Premium Cards)

import streamlit as st
import plotly.graph_objects as go
import json
import os
from src.config import COLORS
from src.database import (
    get_student_by_id, get_skills, get_interests,
    get_career_goal, save_recommendation,
)
from src.ibm_granite import granite_career_recommendations


def _load_career_data() -> dict:
    path = os.path.join("data", "career_data.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


PROFICIENCY_SCORES = {"Beginner": 25, "Intermediate": 50, "Advanced": 75, "Expert": 100}

DOMAIN_STREAM_MAP = {
    "Technology & Engineering":  ["Science (PCM)", "Engineering", "Computer Science"],
    "Data Science & AI/ML":      ["Science (PCM)", "Engineering", "Computer Science"],
    "Business & Management":     ["Commerce", "Arts / Humanities"],
    "Healthcare & Medicine":     ["Science (PCB)", "Medical"],
    "Creative Arts & Design":    ["Arts / Humanities"],
    "Education & Research":      ["Arts / Humanities", "Science (PCB)", "Science (PCM)"],
    "Finance & Accounting":      ["Commerce", "Engineering"],
    "Sales & Marketing":         ["Commerce", "Arts / Humanities"],
}

DOMAIN_INTEREST_MAP = {
    "Technology & Engineering":  ["programming & coding", "mathematics & statistics"],
    "Data Science & AI/ML":      ["programming & coding", "mathematics & statistics"],
    "Business & Management":     ["business & entrepreneurship", "finance & investment"],
    "Healthcare & Medicine":     ["healthcare & wellness", "biology & life sciences"],
    "Creative Arts & Design":    ["art & design", "music & performing arts"],
    "Education & Research":      ["teaching & mentoring", "writing & literature"],
    "Finance & Accounting":      ["finance & investment", "mathematics & statistics"],
    "Sales & Marketing":         ["business & entrepreneurship", "writing & literature"],
}

REQUIRED_SKILLS = {
    "Technology & Engineering": ["Python", "Java", "Cloud Computing", "DevOps", "System Design"],
    "Data Science & AI/ML":     ["Python", "Machine Learning", "SQL", "Statistical Analysis"],
    "Business & Management":    ["Business Analysis", "Leadership", "Financial Modeling", "Project Management"],
    "Healthcare & Medicine":    ["Research", "Critical Thinking", "Data Analysis"],
    "Creative Arts & Design":   ["Storytelling", "Presentation Skills", "Technical Writing"],
    "Finance & Accounting":     ["Financial Modeling", "Data Analysis", "Critical Thinking"],
    "Education & Research":     ["Research", "Technical Writing", "Statistical Analysis"],
    "Sales & Marketing":        ["Public Speaking", "Negotiation", "Data Analysis"],
}

# Domain-specific certifications
DOMAIN_CERTS = {
    "Technology & Engineering": ["AWS Certified Solutions Architect", "Google Cloud Professional", "CKAD (Kubernetes)", "Oracle Java SE"],
    "Data Science & AI/ML":     ["IBM Data Science Professional", "Google Data Analytics", "TensorFlow Developer", "Databricks Associate"],
    "Business & Management":    ["PMP (Project Management)", "CAPM", "Scrum Master (CSM)", "Google Project Management"],
    "Healthcare & Medicine":    ["USMLE (if medicine)", "CPR & First Aid", "Clinical Research Coordinator"],
    "Creative Arts & Design":   ["Google UX Design", "Adobe Certified Professional", "Canva Design"],
    "Finance & Accounting":     ["CA / CPA", "CFA Level 1", "ACCA", "Financial Modelling (FMVA)"],
    "Education & Research":     ["CELTA / TEFL", "Google Certified Educator", "Coursera Teaching"],
    "Sales & Marketing":        ["Google Ads Certified", "HubSpot Marketing", "Meta Blueprint", "Salesforce Admin"],
}

# Career growth outlook
DOMAIN_GROWTH = {
    "Technology & Engineering":  {"growth": "+28%", "jobs": "200K+", "horizon": "5 years"},
    "Data Science & AI/ML":      {"growth": "+45%", "jobs": "150K+", "horizon": "5 years"},
    "Business & Management":     {"growth": "+15%", "jobs": "300K+", "horizon": "5 years"},
    "Healthcare & Medicine":     {"growth": "+22%", "jobs": "500K+", "horizon": "5 years"},
    "Creative Arts & Design":    {"growth": "+18%", "jobs": "80K+",  "horizon": "5 years"},
    "Education & Research":      {"growth": "+12%", "jobs": "400K+", "horizon": "5 years"},
    "Finance & Accounting":      {"growth": "+20%", "jobs": "250K+", "horizon": "5 years"},
    "Sales & Marketing":         {"growth": "+25%", "jobs": "350K+", "horizon": "5 years"},
}

DOMAIN_ICONS = {
    "Technology & Engineering":  "💻",
    "Data Science & AI/ML":      "🤖",
    "Business & Management":     "📊",
    "Healthcare & Medicine":     "🏥",
    "Creative Arts & Design":    "🎨",
    "Education & Research":      "🎓",
    "Finance & Accounting":      "💰",
    "Sales & Marketing":         "📣",
}

DOMAIN_COLORS = {
    "Technology & Engineering":  ("#4F46E5", "#7C3AED"),
    "Data Science & AI/ML":      ("#7C3AED", "#EC4899"),
    "Business & Management":     ("#06B6D4", "#3B82F6"),
    "Healthcare & Medicine":     ("#10B981", "#06B6D4"),
    "Creative Arts & Design":    ("#F59E0B", "#EF4444"),
    "Education & Research":      ("#3B82F6", "#4F46E5"),
    "Finance & Accounting":      ("#10B981", "#3B82F6"),
    "Sales & Marketing":         ("#EF4444", "#F59E0B"),
}


def _score(domain: str, skills: list[dict], interests: list[str], stream: str) -> float:
    score = 0.0
    skill_names = {s["skill_name"].lower() for s in skills}
    interest_lower = {i.lower() for i in interests}
    required = [s.lower() for s in REQUIRED_SKILLS.get(domain, [])]
    score += min(len(skill_names & set(required)) * 15, 45)
    relevant_interests = {i.lower() for i in DOMAIN_INTEREST_MAP.get(domain, [])}
    score += min(len(interest_lower & relevant_interests) * 20, 35)
    if stream and stream in DOMAIN_STREAM_MAP.get(domain, []):
        score += 20
    return round(min(score, 100), 1)


def _score_label(score: float) -> tuple:
    if score >= 75:
        return ("Excellent Match", "#10B981")
    elif score >= 55:
        return ("Good Match", "#06B6D4")
    elif score >= 35:
        return ("Moderate Match", "#F59E0B")
    else:
        return ("Developing Match", "#94A3B8")


def render_career_recommendations(student_id: int | None):
    st.markdown("## 🎯 Career Recommendations")
    st.markdown("AI-powered career path matching — scored against your unique profile.")

    if not student_id:
        st.warning("👤 Please complete your **Student Profile** first.")
        _generic_view()
        return

    student = get_student_by_id(student_id)
    skills = get_skills(student_id)
    interests = get_interests(student_id)
    career_data = _load_career_data()

    # Student summary strip
    st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(79,70,229,0.1),rgba(6,182,212,0.05));
            border:1px solid rgba(79,70,229,0.25);border-radius:12px;padding:0.85rem 1.2rem;
            margin-bottom:1rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap;">
    <div style="font-size:1.8rem;">👤</div>
    <div>
        <div style="color:#E2E8F0;font-weight:700;font-size:1rem;">{student['name']}</div>
        <div style="color:#94A3B8;font-size:0.8rem;">
            {student.get('education','—')} · {student.get('stream','—')} · {len(skills)} skills · {len(interests)} interests
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # Score all domains
    scores = {
        d: _score(d, skills, interests, student.get("stream", ""))
        for d in REQUIRED_SKILLS
    }
    sorted_domains = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Save top recommendation
    if sorted_domains:
        top_d, top_s = sorted_domains[0]
        top_data = career_data.get("career_paths", {}).get(top_d, {})
        save_recommendation(student_id, {
            "domain": top_d,
            "roles": top_data.get("roles", []),
            "score": top_s,
            "reasoning": f"Best match ({top_s}%) based on skills, interests, and stream.",
        })

    # ── Top 3 Medal Cards ─────────────────────────────────────────────────────
    st.markdown("### 🏆 Top Career Matches")
    top3 = sorted_domains[:3]
    cols = st.columns(3, gap="medium")
    medals = [("🥇", "#F59E0B"), ("🥈", "#94A3B8"), ("🥉", "#CD7F32")]
    for idx, (domain, score) in enumerate(top3):
        data = career_data.get("career_paths", {}).get(domain, {})
        demand = data.get("demand_growth", "N/A")
        demand_color = {"Very High": "#10B981", "High": "#06B6D4",
                        "Medium-High": "#F59E0B", "Medium": "#F59E0B",
                        "Stable": "#94A3B8"}.get(demand, "#94A3B8")
        label, label_color = _score_label(score)
        c1, c2 = DOMAIN_COLORS.get(domain, ("#4F46E5", "#7C3AED"))
        icon = DOMAIN_ICONS.get(domain, "🎯")
        growth = DOMAIN_GROWTH.get(domain, {})
        roles_preview = ", ".join(data.get("roles", [])[:2]) if data.get("roles") else "Multiple roles"
        med_emoji, med_color = medals[idx]

        with cols[idx]:
            st.markdown(f"""
<div style="
    background: linear-gradient(145deg, #1E293B, #0F172A);
    border: 1px solid #334155;
    border-top: 3px solid {c1};
    border-radius: 16px;
    padding: 1.4rem;
    position: relative;
    overflow: hidden;
    min-height: 300px;
">
    <div style="position:absolute;top:0;right:0;width:100px;height:100px;
                background:radial-gradient(circle, {c1}20 0%, transparent 70%);"></div>
    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.8rem;">
        <span style="font-size:1.8rem;">{med_emoji}</span>
        <span style="font-size:1.5rem;">{icon}</span>
        <div>
            <div style="color:#E2E8F0;font-weight:700;font-size:0.95rem;">{domain}</div>
            <div style="color:{demand_color};font-size:0.7rem;font-weight:600;">📈 {demand} Demand</div>
        </div>
    </div>
    <div style="text-align:center;margin:0.8rem 0;">
        <div style="font-size:2.6rem;font-weight:800;background:linear-gradient(135deg,{c1},{c2});
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;">{score}%</div>
        <div style="color:{label_color};font-size:0.78rem;font-weight:600;
                    background:{label_color}18;border:1px solid {label_color}40;
                    border-radius:20px;display:inline-block;padding:0.15rem 0.65rem;
                    margin-top:0.2rem;">{label}</div>
    </div>
    <div style="border-top:1px solid #334155;padding-top:0.7rem;margin-top:0.5rem;">
        <div style="color:#94A3B8;font-size:0.73rem;margin-bottom:0.3rem;">Key Roles:</div>
        <div style="color:#E2E8F0;font-size:0.8rem;">{roles_preview}</div>
        <div style="display:flex;gap:0.5rem;margin-top:0.6rem;flex-wrap:wrap;">
            <div style="background:#1E293B;border:1px solid #334155;border-radius:6px;
                        padding:0.2rem 0.55rem;font-size:0.7rem;color:#94A3B8;">
                🚀 {growth.get('growth','N/A')} growth
            </div>
            <div style="background:#1E293B;border:1px solid #334155;border-radius:6px;
                        padding:0.2rem 0.55rem;font-size:0.7rem;color:#94A3B8;">
                💼 {growth.get('jobs','N/A')} openings
            </div>
        </div>
        <div style="color:#94A3B8;font-size:0.7rem;margin-top:0.5rem;">
            Avg ₹{data.get('avg_salary_inr',0)//100000}L/year
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("")

    # ── Bar chart ─────────────────────────────────────────────────────────────
    st.markdown("### 📊 Full Compatibility Analysis")
    domains_list = [d for d, _ in sorted_domains]
    scores_list  = [s for _, s in sorted_domains]
    bar_colors   = [DOMAIN_COLORS.get(d, ("#4F46E5", "#7C3AED"))[0] if i < 3 else "#334155"
                    for i, d in enumerate(domains_list)]
    fig = go.Figure(go.Bar(
        y=domains_list, x=scores_list, orientation="h",
        marker_color=bar_colors,
        text=[f"{s}%" for s in scores_list], textposition="outside",
        hovertemplate="<b>%{y}</b><br>Compatibility: %{x}%<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#0A0F1E", paper_bgcolor="#0A0F1E", font_color="#E2E8F0",
        xaxis=dict(range=[0, 115], gridcolor="#1E293B", title="Compatibility Score (%)"),
        yaxis=dict(gridcolor="#1E293B"),
        height=380, margin=dict(l=10, r=40, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Detailed Domain Cards (all 8) ─────────────────────────────────────────
    st.markdown("### 🃏 All Career Domains — Detailed View")
    for i in range(0, len(sorted_domains), 2):
        pair = sorted_domains[i:i+2]
        cols = st.columns(2, gap="medium")
        for ci, (domain, score) in enumerate(pair):
            data = career_data.get("career_paths", {}).get(domain, {})
            label, label_color = _score_label(score)
            c1, c2 = DOMAIN_COLORS.get(domain, ("#4F46E5", "#7C3AED"))
            icon = DOMAIN_ICONS.get(domain, "🎯")
            certs = DOMAIN_CERTS.get(domain, [])
            growth = DOMAIN_GROWTH.get(domain, {})
            skill_match = len({s["skill_name"].lower() for s in skills} &
                              {sk.lower() for sk in REQUIRED_SKILLS.get(domain, [])})
            skill_total = len(REQUIRED_SKILLS.get(domain, []))
            with cols[ci]:
                st.markdown(f"""
<div style="background:linear-gradient(145deg,#1E293B,#0F172A);border:1px solid #334155;
            border-left:4px solid {c1};border-radius:14px;padding:1.2rem;margin-bottom:0.8rem;">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.8rem;">
        <div style="display:flex;align-items:center;gap:0.5rem;">
            <span style="font-size:1.5rem;">{icon}</span>
            <div>
                <div style="color:#E2E8F0;font-weight:700;font-size:0.95rem;">{domain}</div>
                <div style="color:{label_color};font-size:0.72rem;font-weight:600;">{label}</div>
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:1.8rem;font-weight:800;color:{c1};">{score}%</div>
            <div style="color:#94A3B8;font-size:0.7rem;">match</div>
        </div>
    </div>
    <!-- Score bar -->
    <div style="background:#0A0F1E;border-radius:4px;height:6px;margin-bottom:0.8rem;">
        <div style="background:linear-gradient(90deg,{c1},{c2});height:6px;border-radius:4px;width:{score}%;"></div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;font-size:0.78rem;">
        <div>
            <div style="color:#94A3B8;font-size:0.68rem;margin-bottom:0.2rem;">KEY ROLES</div>
            {"".join(f'<div style="color:#E2E8F0;padding:1px 0;">• {r}</div>' for r in data.get('roles',['—'])[:3])}
        </div>
        <div>
            <div style="color:#94A3B8;font-size:0.68rem;margin-bottom:0.2rem;">CERTIFICATIONS</div>
            {"".join(f'<div style="color:#06B6D4;padding:1px 0;">✦ {c}</div>' for c in certs[:3])}
        </div>
    </div>
    <div style="display:flex;gap:0.5rem;margin-top:0.75rem;flex-wrap:wrap;">
        <div style="background:#0A0F1E;border:1px solid #334155;border-radius:6px;
                    padding:0.2rem 0.6rem;font-size:0.7rem;color:#10B981;">
            🚀 {growth.get('growth','N/A')}
        </div>
        <div style="background:#0A0F1E;border:1px solid #334155;border-radius:6px;
                    padding:0.2rem 0.6rem;font-size:0.7rem;color:#F59E0B;">
            💼 {growth.get('jobs','N/A')} jobs
        </div>
        <div style="background:#0A0F1E;border:1px solid #334155;border-radius:6px;
                    padding:0.2rem 0.6rem;font-size:0.7rem;color:#94A3B8;">
            🛠 {skill_match}/{skill_total} skills met
        </div>
        <div style="background:#0A0F1E;border:1px solid #334155;border-radius:6px;
                    padding:0.2rem 0.6rem;font-size:0.7rem;color:#94A3B8;">
            💰 ₹{data.get('avg_salary_inr',0)//100000}L/yr avg
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── IBM Granite AI recommendations ────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🤖 IBM Granite AI — Deep Career Analysis")
    st.markdown("Get a personalised, detailed career analysis powered by IBM Granite.")
    if st.button("🚀 Generate IBM Granite AI Analysis", use_container_width=True):
        with st.spinner("IBM Granite is analysing your profile..."):
            skill_names = [s["skill_name"] for s in skills]
            ai_text = granite_career_recommendations(
                student.get("education", ""), student.get("stream", ""),
                skill_names, interests,
            )
        st.markdown(f"""
<div style="background:#1E293B;border:1px solid rgba(79,70,229,0.4);border-radius:12px;
            padding:1.2rem;border-left:4px solid #4F46E5;">
{ai_text}
</div>
""", unsafe_allow_html=True)

    # ── Domain deep-dive ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔍 Domain Deep Dive")
    selected = st.selectbox("Select a domain to explore in detail:", [d for d, _ in sorted_domains])
    _domain_detail(selected, career_data, scores.get(selected, 0))


def _domain_detail(domain: str, career_data: dict, score: float):
    data = career_data.get("career_paths", {}).get(domain, {})
    c1, c2 = DOMAIN_COLORS.get(domain, ("#4F46E5", "#7C3AED"))
    certs = DOMAIN_CERTS.get(domain, [])
    growth = DOMAIN_GROWTH.get(domain, {})
    label, label_color = _score_label(score)

    if not data:
        st.info("Detailed data not available for this domain.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:10px;padding:1rem;">
    <h4 style="color:#06B6D4;margin-top:0;font-size:0.9rem;">🎭 Key Roles</h4>
    {"".join(f'<div style="padding:3px 0;color:#E2E8F0;font-size:0.85rem;">• {r}</div>' for r in data.get('roles',[]))}
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:10px;padding:1rem;">
    <h4 style="color:#10B981;margin-top:0;font-size:0.9rem;">🛠️ Required Skills</h4>
    {"".join(f'<div style="padding:3px 0;color:#E2E8F0;font-size:0.85rem;">• {s}</div>' for s in data.get('top_skills',[]))}
</div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:10px;padding:1rem;">
    <h4 style="color:#F59E0B;margin-top:0;font-size:0.9rem;">📜 Certifications</h4>
    {"".join(f'<div style="padding:3px 0;color:#06B6D4;font-size:0.82rem;">✦ {c}</div>' for c in certs[:5])}
</div>""", unsafe_allow_html=True)

    col4, col5 = st.columns(2)
    with col4:
        st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:10px;padding:1rem;margin-top:0.8rem;">
    <h4 style="color:#EF4444;margin-top:0;font-size:0.9rem;">🏢 Top Companies</h4>
    {"".join(f'<div style="padding:3px 0;color:#E2E8F0;font-size:0.85rem;">• {c}</div>' for c in data.get('top_companies',[]))}
</div>""", unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:10px;padding:1rem;margin-top:0.8rem;">
    <h4 style="color:#7C3AED;margin-top:0;font-size:0.9rem;">📈 Growth Outlook</h4>
    <div style="color:#10B981;font-weight:700;font-size:1.2rem;">{growth.get('growth','N/A')} YoY</div>
    <div style="color:#94A3B8;font-size:0.82rem;margin-top:0.3rem;">
        💼 {growth.get('jobs','N/A')} open positions<br>
        🗓 Forecast: next {growth.get('horizon','5 years')}<br>
        💰 ₹{data.get('avg_salary_inr',0)//100000}L/year avg salary<br>
        📈 {data.get('demand_growth','N/A')} demand
    </div>
    <div style="margin-top:0.6rem;">
        <div style="color:#94A3B8;font-size:0.78rem;margin-bottom:0.2rem;">Education Paths:</div>
        {"".join(f'<div style="color:#E2E8F0;font-size:0.8rem;padding:1px 0;">• {e}</div>' for e in data.get('education',[])[:3])}
    </div>
</div>""", unsafe_allow_html=True)


def _generic_view():
    st.markdown("---")
    st.markdown("### 🌐 Popular Career Domains — India 2025")
    career_data = _load_career_data()
    cols = st.columns(2, gap="medium")
    items = list(career_data.get("career_paths", {}).items())[:4]
    for i, (domain, data) in enumerate(items):
        c1, c2 = DOMAIN_COLORS.get(domain, ("#4F46E5", "#7C3AED"))
        icon = DOMAIN_ICONS.get(domain, "🎯")
        growth = DOMAIN_GROWTH.get(domain, {})
        with cols[i % 2]:
            with st.expander(f"{icon} **{domain}** — ₹{data.get('avg_salary_inr',0)//100000}L/yr"):
                st.markdown(f"""
<div style="font-size:0.85rem;color:#E2E8F0;">
    <div style="margin-bottom:0.4rem;"><span style="color:#06B6D4;">Roles:</span> {', '.join(data.get('roles',[]))}</div>
    <div style="margin-bottom:0.4rem;"><span style="color:#10B981;">Skills:</span> {', '.join(data.get('top_skills',[]))}</div>
    <div><span style="color:#F59E0B;">Growth:</span> {growth.get('growth','N/A')} | {growth.get('jobs','N/A')} openings</div>
</div>
""", unsafe_allow_html=True)
