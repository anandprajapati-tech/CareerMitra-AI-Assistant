# modules/career_roadmap.py
# CareerMitra AI – Career Roadmap Generator

import streamlit as st
import plotly.graph_objects as go
from config.settings import CAREER_DOMAINS, COLORS
from database.db_manager import (
    get_student_by_id, get_career_goal, get_latest_recommendation,
    save_career_goal, get_skills
)

# ── Static roadmap templates keyed by career domain ───────────────────────────
ROADMAP_TEMPLATES = {
    "Technology & Engineering": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Learn Python / Java fundamentals",
            "Complete Data Structures & Algorithms (DSA) basics",
            "Set up GitHub profile and commit daily",
            "Build 2 small projects (calculator, to-do app)",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Complete an OS, Networks, and DBMS course",
            "Learn SQL and work with databases",
            "Contribute to 1 open-source project",
            "Solve 150+ LeetCode problems",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Choose specialisation: Backend, DevOps, Cloud, or Embedded",
            "Get AWS / GCP / Azure Cloud certification",
            "Build a full-stack capstone project",
            "Apply for internships or entry-level roles",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Land a Software Engineer role at a target company",
            "Clear technical interviews (System Design, DSA)",
            "Build a professional network on LinkedIn",
            "Plan for senior-level certifications in 2 years",
        ]},
    ],
    "Data Science & AI/ML": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Master Python (NumPy, Pandas, Matplotlib)",
            "Learn Statistics & Probability fundamentals",
            "Complete Andrew Ng's ML course on Coursera",
            "Participate in 2 Kaggle competitions",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Learn SQL for data analysis",
            "Study Deep Learning (CNNs, RNNs, Transformers)",
            "Build a data science portfolio with 3 projects",
            "Get Google Data Analytics or IBM Data Science certificate",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Specialise in NLP, Computer Vision, or MLOps",
            "Deploy ML models to production (FastAPI / Docker)",
            "Learn cloud ML services (AWS SageMaker / Vertex AI)",
            "Apply for data analyst / junior data scientist roles",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Secure a Data Scientist or ML Engineer position",
            "Contribute to published research or blog posts",
            "Mentor junior data enthusiasts",
            "Explore advanced certifications (TensorFlow, Databricks)",
        ]},
    ],
    "Business & Management": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Understand core business concepts (marketing, finance, ops)",
            "Learn Excel and basic financial modeling",
            "Start reading business books (Good to Great, Zero to One)",
            "Join a case study competition or business club",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Learn project management basics (PMP / Agile)",
            "Study business analytics with Power BI or Tableau",
            "Complete an internship in a business function",
            "Build a LinkedIn profile and grow your network",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Prepare for CAT / GMAT for an MBA",
            "Specialise in consulting, product, or operations",
            "Complete a strategy or consulting internship",
            "Get PMP or CAPM certification",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Join a top-tier MBA program or enter management trainee",
            "Land an analyst role at a consulting / product firm",
            "Lead a cross-functional project",
            "Build an executive presence on LinkedIn",
        ]},
    ],
    "Healthcare & Medicine": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Complete 10+2 Science (PCB) with strong grades",
            "Enrol for NEET coaching / preparation",
            "Build basics in Biology, Chemistry, and Physics",
            "Shadow a doctor or volunteer at a clinic",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Clear NEET UG and secure MBBS admission",
            "Focus on Pre-clinical subjects (Anatomy, Physiology)",
            "Join a medical research group",
            "Develop clinical empathy and communication skills",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Complete clinical rotations across all departments",
            "Decide on a specialisation (Cardiology, Neuro, Surgery, etc.)",
            "Prepare for NEET PG / USMLE if considering abroad",
            "Publish a case study or research paper",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Complete MD/MS residency",
            "Register with MCI / NMC",
            "Start practice or join a hospital",
            "Consider fellowship or super-specialisation",
        ]},
    ],
    "Finance & Accounting": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Learn accounting basics: P&L, Balance Sheet, Cash Flow",
            "Master Excel (VLOOKUP, Pivot Tables, Macros)",
            "Start CA Foundation / CFA Level 1 preparation",
            "Open a Demat account and study the stock market",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Complete CA Intermediate / CFA Level 1",
            "Learn financial modeling in Excel",
            "Intern at a CA firm or bank",
            "Get proficient in Tally, QuickBooks, or SAP",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Clear CA Final / CFA Level 2",
            "Choose track: Audit, Tax, Investment Banking, or Corporate Finance",
            "Build a network in ICAI / CFA Institute communities",
            "Complete an MBA Finance if targeting investment banking",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Join a Big 4 firm, bank, or hedge fund",
            "Obtain full CA / CFA / CPA designation",
            "Manage a financial portfolio or audit team",
            "Plan for senior management or CFO track",
        ]},
    ],
}

# Fallback for domains not in templates
DEFAULT_ROADMAP = [
    {"phase": "Foundation (0–6 months)", "milestones": [
        "Research the field and identify key sub-domains",
        "Take a foundational online course on Coursera / edX",
        "Connect with 5 professionals in the field on LinkedIn",
        "Set clear short-term and long-term goals",
    ]},
    {"phase": "Skill Building (6–18 months)", "milestones": [
        "Complete 2 certifications relevant to your domain",
        "Build a portfolio or proof-of-work project",
        "Attend industry events or webinars",
        "Find a mentor in your target field",
    ]},
    {"phase": "Specialisation (18–30 months)", "milestones": [
        "Narrow focus to a high-demand sub-specialisation",
        "Complete an internship or part-time role",
        "Contribute to a community or publish content",
        "Apply for full-time roles or advanced programs",
    ]},
    {"phase": "Career Launch (30+ months)", "milestones": [
        "Secure an entry-to-mid level role in your target domain",
        "Build reputation through quality work and networking",
        "Plan for the next seniority level",
        "Give back by mentoring the next generation",
    ]},
]


def render_career_roadmap(student_id: int | None):
    """Render the Career Roadmap page."""
    st.markdown("## 🗺️ Career Roadmap")
    st.markdown("Your personalised, step-by-step journey to career success.")

    if not student_id:
        st.warning("👤 Please complete your **Student Profile** first to generate a personalised roadmap.")
        _render_generic_roadmap()
        return

    student = get_student_by_id(student_id)
    goal = get_career_goal(student_id)
    rec = get_latest_recommendation(student_id)

    # ── Goal setup ─────────────────────────────────────────────────────────────
    st.markdown("### 🎯 Set Your Career Goal")
    with st.form("career_goal_form"):
        col1, col2 = st.columns(2)
        with col1:
            selected_domain = st.selectbox(
                "Target Career Domain:",
                CAREER_DOMAINS,
                index=CAREER_DOMAINS.index(goal["goal_domain"]) if goal and goal.get("goal_domain") in CAREER_DOMAINS else 0,
            )
            target_role = st.text_input("Target Job Role:", value=goal.get("target_role", "") if goal else "")
        with col2:
            timeline = st.selectbox(
                "Target Timeline:",
                ["6 months", "1 year", "2 years", "3 years", "5 years"],
                index=1,
            )
            notes = st.text_area("Notes / Motivation:", value=goal.get("notes", "") if goal else "", height=80)
        submitted = st.form_submit_button("💾 Save Goal & Generate Roadmap", use_container_width=True)
        if submitted:
            save_career_goal(student_id, {"domain": selected_domain, "role": target_role, "timeline": timeline, "notes": notes})
            st.success(f"✅ Goal saved! Generating roadmap for **{selected_domain}**…")
            st.rerun()

    # ── Render roadmap ─────────────────────────────────────────────────────────
    if goal:
        domain = goal.get("goal_domain") or (rec.get("career_domain") if rec else None)
        roadmap = ROADMAP_TEMPLATES.get(domain, DEFAULT_ROADMAP)
        st.markdown(f"### 🗺️ Roadmap: **{domain}** → *{goal.get('target_role', 'Your target role')}*")
        _render_roadmap_timeline(roadmap)
    else:
        st.info("📌 Set your career goal above to generate your personalised roadmap.")


def _render_roadmap_timeline(roadmap: list[dict]):
    phase_colors = [COLORS["primary"], COLORS["secondary"], COLORS["accent"], COLORS["success"]]
    for i, phase in enumerate(roadmap):
        color = phase_colors[i % len(phase_colors)]
        with st.expander(f"**{phase['phase']}**", expanded=(i == 0)):
            for milestone in phase["milestones"]:
                st.markdown(f"""
<div style="display:flex; align-items:flex-start; gap:0.75rem; padding:0.5rem 0; border-bottom:1px solid #1E293B;">
    <div style="width:10px; height:10px; border-radius:50%; background:{color}; margin-top:5px; flex-shrink:0;"></div>
    <span style="color:#F1F5F9;">{milestone}</span>
</div>""", unsafe_allow_html=True)


def _render_generic_roadmap():
    st.markdown("---")
    st.markdown("### 🛣️ Sample Career Roadmap (Technology)")
    roadmap = ROADMAP_TEMPLATES.get("Technology & Engineering", DEFAULT_ROADMAP)
    _render_roadmap_timeline(roadmap)
