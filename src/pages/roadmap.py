# src/pages/roadmap.py
# CareerMitra AI – Career Roadmap Page (IBM Granite enhanced)

import streamlit as st
from src.config import CAREER_DOMAINS, COLORS
from src.database import (
    get_student_by_id, get_career_goal, get_latest_recommendation,
    save_career_goal, get_skills,
)
from src.ibm_granite import granite_roadmap

ROADMAP_TEMPLATES = {
    "Technology & Engineering": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Learn Python / Java fundamentals — freeCodeCamp or CS50",
            "Complete Data Structures & Algorithms basics",
            "Set up GitHub profile and commit daily",
            "Build 2 small projects (calculator, to-do app)",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Study OS, Networks, and Databases",
            "Learn SQL and build database-backed apps",
            "Solve 150+ LeetCode problems",
            "Contribute to 1 open-source project",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Choose: Backend, DevOps, Cloud, or Embedded",
            "Earn AWS / GCP / Azure Cloud certification",
            "Build a full-stack capstone project",
            "Apply for internships or entry-level roles",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Land a Software Engineer role at a target company",
            "Clear DSA + System Design interviews",
            "Build professional network on LinkedIn",
            "Plan senior-level certifications in 2 years",
        ]},
    ],
    "Data Science & AI/ML": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Master Python (NumPy, Pandas, Matplotlib)",
            "Complete Andrew Ng's ML course on Coursera",
            "Learn Statistics & Probability fundamentals",
            "Participate in 2 Kaggle competitions",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Learn SQL for data analysis",
            "Study Deep Learning (CNNs, RNNs, Transformers)",
            "Build 3 portfolio projects on GitHub",
            "Get Google Data Analytics or IBM Data Science certificate",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Specialise in NLP, Computer Vision, or MLOps",
            "Deploy ML models with FastAPI and Docker",
            "Learn cloud ML (AWS SageMaker / Vertex AI)",
            "Apply for data analyst / junior data scientist roles",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Secure Data Scientist or ML Engineer position",
            "Contribute to published research or tech blog",
            "Mentor junior data enthusiasts",
            "Explore advanced certifications (TensorFlow, Databricks)",
        ]},
    ],
    "Business & Management": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Learn core business concepts (marketing, finance, ops)",
            "Master Excel and basic financial modeling",
            "Read business classics (Good to Great, Zero to One)",
            "Join a case study club or debate team",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Learn project management (Agile / Scrum basics)",
            "Build Power BI or Tableau data skills",
            "Complete an internship in a business function",
            "Grow your LinkedIn network to 200+ connections",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Prepare for CAT / GMAT for MBA admission",
            "Choose: Consulting, Product, or Operations track",
            "Complete a strategy internship",
            "Earn PMP or CAPM certification",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Join a top MBA program or management trainee scheme",
            "Land an analyst role at a consulting / product firm",
            "Lead a cross-functional project",
            "Build executive presence through thought leadership",
        ]},
    ],
    "Finance & Accounting": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Learn accounting basics: P&L, Balance Sheet, Cash Flow",
            "Master Excel (VLOOKUP, Pivot Tables, Macros)",
            "Start CA Foundation / CFA Level 1 prep",
            "Open a Demat account and study the stock market",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Complete CA Intermediate / CFA Level 1",
            "Build financial models in Excel",
            "Intern at a CA firm or bank",
            "Learn Tally, QuickBooks, or SAP basics",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Clear CA Final / CFA Level 2",
            "Choose: Audit, Tax, IB, or Corporate Finance",
            "Build ICAI / CFA community network",
            "Complete MBA Finance if targeting investment banking",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Join a Big 4 firm, bank, or hedge fund",
            "Obtain full CA / CFA / CPA designation",
            "Manage a financial portfolio or audit team",
            "Chart a path toward CFO / senior finance track",
        ]},
    ],
}

DEFAULT_ROADMAP = [
    {"phase": "Foundation (0–6 months)", "milestones": [
        "Research the field and identify 3 key sub-domains",
        "Take a foundational course on Coursera or edX",
        "Connect with 5 professionals on LinkedIn",
        "Set SMART short-term and long-term goals",
    ]},
    {"phase": "Skill Building (6–18 months)", "milestones": [
        "Complete 2 relevant certifications",
        "Build a portfolio or proof-of-work project",
        "Attend industry events or virtual webinars",
        "Find a mentor in your target field",
    ]},
    {"phase": "Specialisation (18–30 months)", "milestones": [
        "Narrow focus to a high-demand sub-specialisation",
        "Complete an internship or part-time role",
        "Contribute to a community or publish content",
        "Apply for full-time roles or advanced programs",
    ]},
    {"phase": "Career Launch (30+ months)", "milestones": [
        "Secure an entry-to-mid level role in your domain",
        "Build reputation through quality work & networking",
        "Plan for the next seniority level",
        "Give back by mentoring the next generation",
    ]},
]


def render_career_roadmap(student_id: int | None):
    st.markdown("## 🗺️ Career Roadmap")
    st.markdown("Your step-by-step journey to career success — enhanced by IBM Granite AI.")

    if not student_id:
        st.warning("👤 Complete your **Student Profile** first.")
        _generic_roadmap()
        return

    goal = get_career_goal(student_id)
    rec  = get_latest_recommendation(student_id)
    skills = get_skills(student_id)

    st.markdown("### 🎯 Set / Update Your Goal")
    with st.form("goal_form"):
        c1, c2 = st.columns(2)
        with c1:
            domain = st.selectbox("Target Domain:", CAREER_DOMAINS,
                index=CAREER_DOMAINS.index(goal["goal_domain"])
                if goal and goal.get("goal_domain") in CAREER_DOMAINS else 0)
            target_role = st.text_input("Target Role:", value=goal.get("target_role","") if goal else "")
        with c2:
            timeline = st.selectbox("Timeline:", ["6 months","1 year","2 years","3 years","5 years"], index=1)
            notes = st.text_area("Notes:", value=goal.get("notes","") if goal else "", height=80)
        if st.form_submit_button("💾 Save Goal", use_container_width=True):
            save_career_goal(student_id, {"domain": domain, "role": target_role,
                                          "timeline": timeline, "notes": notes})
            st.success("✅ Goal saved!")
            st.rerun()

    if goal:
        d = goal.get("goal_domain") or (rec.get("career_domain") if rec else None)
        roadmap = ROADMAP_TEMPLATES.get(d, DEFAULT_ROADMAP)
        st.markdown(f"### 🗺️ Roadmap: **{d}** → *{goal.get('target_role','Your role')}*")
        _render_timeline(roadmap)

        # IBM Granite AI roadmap
        st.markdown("---")
        st.markdown("### 🤖 IBM Granite Personalised Roadmap")
        if st.button("Generate AI Roadmap", use_container_width=True):
            skill_names = [s["skill_name"] for s in skills]
            with st.spinner("IBM Granite is generating your roadmap..."):
                ai_text = granite_roadmap(d or "Technology & Engineering",
                                          goal.get("target_role",""),
                                          goal.get("target_timeline","2 years"),
                                          skill_names)
            st.markdown(ai_text)
    else:
        st.info("📌 Set your career goal above to generate your roadmap.")


def _render_timeline(roadmap: list[dict]):
    phase_colors = [COLORS["primary"], COLORS["secondary"], COLORS["accent"], COLORS["success"]]
    for i, phase in enumerate(roadmap):
        color = phase_colors[i % len(phase_colors)]
        with st.expander(f"**{phase['phase']}**", expanded=(i == 0)):
            for m in phase["milestones"]:
                st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:0.6rem;padding:0.4rem 0;border-bottom:1px solid #1E293B;">
    <div style="width:9px;height:9px;border-radius:50%;background:{color};margin-top:5px;flex-shrink:0;"></div>
    <span style="color:#F1F5F9;">{m}</span>
</div>""", unsafe_allow_html=True)


def _generic_roadmap():
    st.markdown("---")
    st.markdown("### 🛣️ Sample Roadmap: Technology & Engineering")
    _render_timeline(ROADMAP_TEMPLATES.get("Technology & Engineering", DEFAULT_ROADMAP))
