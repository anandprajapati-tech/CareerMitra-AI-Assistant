# modules/job_market_insights.py
# CareerMitra AI – Job Market Insights Module

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config.settings import COLORS


# ── Static market data (updated with 2024–2025 Indian & global figures) ───────
JOB_MARKET_DATA = {
    "demand_trends": {
        "Data Science & AI/ML": 92,
        "Cloud & DevOps": 88,
        "Cybersecurity": 85,
        "Full Stack Development": 82,
        "Product Management": 78,
        "Digital Marketing": 72,
        "Business Analysis": 68,
        "Finance & FinTech": 74,
        "Healthcare Tech": 76,
        "UX/UI Design": 65,
    },
    "salary_ranges_inr": {
        "Data Scientist": {"min": 800000, "max": 3000000, "median": 1500000},
        "ML Engineer": {"min": 1000000, "max": 3500000, "median": 1800000},
        "Software Engineer (3 yrs)": {"min": 700000, "max": 2500000, "median": 1200000},
        "Cloud Engineer": {"min": 900000, "max": 2800000, "median": 1400000},
        "Product Manager": {"min": 1200000, "max": 4000000, "median": 2200000},
        "Business Analyst": {"min": 600000, "max": 1800000, "median": 1000000},
        "UX Designer": {"min": 500000, "max": 1800000, "median": 900000},
        "Digital Marketer": {"min": 400000, "max": 1500000, "median": 700000},
        "Chartered Accountant": {"min": 700000, "max": 2500000, "median": 1200000},
        "Doctor (Specialist)": {"min": 1200000, "max": 5000000, "median": 2500000},
    },
    "top_hiring_cities": {
        "Bengaluru": 28,
        "Hyderabad": 18,
        "Mumbai": 16,
        "Pune": 12,
        "Chennai": 10,
        "Delhi NCR": 9,
        "Kolkata": 4,
        "Others": 3,
    },
    "top_companies_hiring": [
        {"company": "Google India", "roles": 1200, "domain": "Tech/AI"},
        {"company": "Microsoft India", "roles": 1500, "domain": "Cloud/Dev"},
        {"company": "Amazon India", "roles": 3200, "domain": "E-commerce/Cloud"},
        {"company": "Infosys", "roles": 12000, "domain": "IT Services"},
        {"company": "TCS", "roles": 18000, "domain": "IT Services"},
        {"company": "Wipro", "roles": 8000, "domain": "IT Services"},
        {"company": "Flipkart", "roles": 900, "domain": "E-commerce/ML"},
        {"company": "Zomato", "roles": 600, "domain": "Tech/Product"},
        {"company": "Goldman Sachs India", "roles": 700, "domain": "Finance/Tech"},
        {"company": "Apollo Hospitals", "roles": 2000, "domain": "Healthcare"},
    ],
    "skill_demand_2025": {
        "Generative AI / LLMs": 95,
        "Python": 90,
        "Cloud (AWS/GCP/Azure)": 88,
        "SQL / Data Engineering": 82,
        "React / Node.js": 78,
        "Kubernetes / Docker": 76,
        "Cybersecurity Tools": 74,
        "Power BI / Tableau": 70,
        "DevOps / CI-CD": 72,
        "Prompt Engineering": 85,
    },
    "growth_forecast_yoy": {
        "AI/ML Roles": 45,
        "Cloud Engineering": 32,
        "Cybersecurity": 28,
        "FinTech": 25,
        "Healthcare Tech": 22,
        "Digital Marketing": 18,
        "Traditional IT Services": 8,
        "Core Manufacturing": 5,
    },
    "freshers_placement_rate": {
        "IIT Graduates": 96,
        "NIT Graduates": 88,
        "Top Private Engineering": 75,
        "State Engineering Colleges": 55,
        "MBA (IIMs)": 99,
        "MBA (Other Top B-schools)": 80,
        "Medical (AIIMS)": 100,
        "B.Sc / BA / B.Com": 42,
    },
}


def render_job_market_insights(student_id: int | None):
    """Render the Job Market Insights page."""
    st.markdown("## 📈 Job Market Insights")
    st.markdown("Real-time trends, salary benchmarks, and hiring intelligence for the Indian job market (2025).")

    # ── Tabs layout ───────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Demand Trends", "💰 Salary Benchmarks", "🏢 Top Hiring", "🔮 Future Outlook"])

    with tab1:
        _render_demand_trends()

    with tab2:
        _render_salary_benchmarks()

    with tab3:
        _render_top_hiring()

    with tab4:
        _render_future_outlook()


def _render_demand_trends():
    st.markdown("### 📊 Career Domain Demand Index (2025)")
    st.caption("Demand score out of 100 based on job posting volume, growth rate, and employer surveys.")

    demand = JOB_MARKET_DATA["demand_trends"]
    sorted_demand = sorted(demand.items(), key=lambda x: x[1], reverse=True)
    domains = [d for d, _ in sorted_demand]
    scores = [s for _, s in sorted_demand]
    colors_list = [COLORS["success"] if s >= 80 else (COLORS["warning"] if s >= 65 else COLORS["danger"]) for s in scores]

    fig = go.Figure(go.Bar(
        x=scores, y=domains, orientation="h",
        marker_color=colors_list,
        text=[f"{s}/100" for s in scores], textposition="outside",
    ))
    fig.update_layout(
        plot_bgcolor="#0F172A", paper_bgcolor="#0F172A", font_color="#F1F5F9",
        xaxis=dict(range=[0, 110], gridcolor="#334155"),
        yaxis=dict(gridcolor="#334155"),
        height=400, margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🔥 Most In-Demand Skills (2025)")
    skill_demand = JOB_MARKET_DATA["skill_demand_2025"]
    sorted_skills = sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)
    cols = st.columns(2)
    for i, (skill, score) in enumerate(sorted_skills):
        with cols[i % 2]:
            bar_color = COLORS["primary"] if score >= 85 else (COLORS["accent"] if score >= 75 else COLORS["secondary"])
            st.markdown(f"""
<div style="margin-bottom:0.5rem;">
    <div style="display:flex; justify-content:space-between; color:#F1F5F9; font-size:0.85rem; margin-bottom:2px;">
        <span>{skill}</span><span>{score}%</span>
    </div>
    <div style="background:#1E293B; border-radius:4px; height:8px;">
        <div style="background:{bar_color}; height:8px; border-radius:4px; width:{score}%;"></div>
    </div>
</div>""", unsafe_allow_html=True)


def _render_salary_benchmarks():
    st.markdown("### 💰 Salary Ranges (India, 2025)")
    st.caption("Annual CTC in INR for professionals with 2–5 years experience.")

    salary_data = JOB_MARKET_DATA["salary_ranges_inr"]
    roles = list(salary_data.keys())
    medians = [salary_data[r]["median"] / 100000 for r in roles]
    mins = [salary_data[r]["min"] / 100000 for r in roles]
    maxs = [salary_data[r]["max"] / 100000 for r in roles]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Min", x=roles, y=mins, marker_color="#334155"))
    fig.add_trace(go.Bar(name="Median", x=roles, y=medians, marker_color=COLORS["primary"]))
    fig.add_trace(go.Bar(name="Max", x=roles, y=maxs, marker_color=COLORS["accent"]))
    fig.update_layout(
        barmode="group",
        plot_bgcolor="#0F172A", paper_bgcolor="#0F172A", font_color="#F1F5F9",
        yaxis_title="Annual CTC (₹ Lakhs)", xaxis_tickangle=-30,
        legend=dict(bgcolor="#1E293B", bordercolor="#334155"),
        height=420, margin=dict(l=10, r=10, t=10, b=80),
        xaxis=dict(gridcolor="#334155"), yaxis=dict(gridcolor="#334155"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Placement rates
    st.markdown("### 🎓 Fresher Placement Rates by Institution Type")
    placement = JOB_MARKET_DATA["freshers_placement_rate"]
    df = pd.DataFrame(list(placement.items()), columns=["Institution", "Placement Rate (%)"])
    fig2 = px.bar(df, x="Placement Rate (%)", y="Institution", orientation="h",
                  color="Placement Rate (%)", color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"])
    fig2.update_layout(
        plot_bgcolor="#0F172A", paper_bgcolor="#0F172A", font_color="#F1F5F9",
        height=340, margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="#334155"), yaxis=dict(gridcolor="#334155"),
    )
    st.plotly_chart(fig2, use_container_width=True)


def _render_top_hiring():
    st.markdown("### 🏢 Top Hiring Companies in India (2025)")

    companies = JOB_MARKET_DATA["top_companies_hiring"]
    for company in companies:
        col1, col2, col3 = st.columns([3, 1, 2])
        with col1:
            st.markdown(f"**{company['company']}**")
        with col2:
            st.markdown(f"<span style='color:#10B981;'>{company['roles']:,} roles</span>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<span style='color:#94A3B8; font-size:0.85rem;'>{company['domain']}</span>", unsafe_allow_html=True)
        st.divider()

    st.markdown("### 🏙️ Top Hiring Cities")
    cities = JOB_MARKET_DATA["top_hiring_cities"]
    fig = go.Figure(go.Pie(
        labels=list(cities.keys()), values=list(cities.values()),
        hole=0.45, marker_colors=[COLORS["primary"], COLORS["secondary"], COLORS["accent"],
                                   COLORS["success"], COLORS["warning"], "#EC4899", "#F97316", "#94A3B8"],
    ))
    fig.update_layout(
        paper_bgcolor="#0F172A", font_color="#F1F5F9",
        legend=dict(bgcolor="#1E293B", bordercolor="#334155"),
        height=360, margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_future_outlook():
    st.markdown("### 🔮 Year-on-Year Role Growth Forecast (2025–2026)")
    st.caption("Estimated % growth in job openings across domains.")

    growth = JOB_MARKET_DATA["growth_forecast_yoy"]
    sorted_growth = sorted(growth.items(), key=lambda x: x[1], reverse=True)
    domains = [d for d, _ in sorted_growth]
    pct = [g for _, g in sorted_growth]
    colors_list = [COLORS["success"] if p >= 25 else (COLORS["accent"] if p >= 15 else COLORS["warning"]) for p in pct]

    fig = go.Figure(go.Bar(
        x=pct, y=domains, orientation="h",
        marker_color=colors_list,
        text=[f"+{p}%" for p in pct], textposition="outside",
    ))
    fig.update_layout(
        plot_bgcolor="#0F172A", paper_bgcolor="#0F172A", font_color="#F1F5F9",
        xaxis=dict(range=[0, 60], gridcolor="#334155", title="Growth %"),
        yaxis=dict(gridcolor="#334155"),
        height=380, margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🌟 Key Trends to Watch")
    trends = [
        ("🤖 Generative AI Disruption", "AI tools are transforming every sector. Roles requiring AI literacy will see 3x growth by 2027."),
        ("☁️ Cloud-First India", "The Indian cloud market is projected to reach $13B by 2026, driving massive demand for cloud engineers."),
        ("🛡️ Cybersecurity Crisis", "India reports 1.4 million cyber attacks annually. Demand for security professionals outpaces supply by 3:1."),
        ("🏥 HealthTech Boom", "Post-COVID investment in digital health is creating 500K+ new jobs in healthcare technology by 2026."),
        ("🎓 Skill Over Degree", "Top companies like Google, IBM, and Amazon now hire based on skills and certifications, not just degrees."),
    ]
    for title, desc in trends:
        with st.expander(f"**{title}**"):
            st.markdown(desc)
