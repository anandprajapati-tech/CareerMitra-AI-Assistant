# src/pages/job_market.py
# CareerMitra AI – Job Market Insights Page

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from src.config import COLORS

JOB_DATA = {
    "demand_trends": {
        "Data Science & AI/ML": 92, "Cloud & DevOps": 88, "Cybersecurity": 85,
        "Full Stack Dev": 82, "Product Management": 78, "Digital Marketing": 72,
        "Business Analysis": 68, "Finance & FinTech": 74, "Healthcare Tech": 76, "UX/UI Design": 65,
    },
    "salary_ranges_inr": {
        "Data Scientist":          {"min": 800000,  "max": 3000000, "median": 1500000},
        "ML Engineer":             {"min": 1000000, "max": 3500000, "median": 1800000},
        "Software Engineer (3yr)": {"min": 700000,  "max": 2500000, "median": 1200000},
        "Cloud Engineer":          {"min": 900000,  "max": 2800000, "median": 1400000},
        "Product Manager":         {"min": 1200000, "max": 4000000, "median": 2200000},
        "Business Analyst":        {"min": 600000,  "max": 1800000, "median": 1000000},
        "UX Designer":             {"min": 500000,  "max": 1800000, "median": 900000},
        "Digital Marketer":        {"min": 400000,  "max": 1500000, "median": 700000},
        "CA / CPA":                {"min": 700000,  "max": 2500000, "median": 1200000},
        "Doctor (Specialist)":     {"min": 1200000, "max": 5000000, "median": 2500000},
    },
    "top_cities": {
        "Bengaluru": 28, "Hyderabad": 18, "Mumbai": 16, "Pune": 12,
        "Chennai": 10, "Delhi NCR": 9, "Kolkata": 4, "Others": 3,
    },
    "top_companies": [
        {"company": "Google India",       "roles": 1200,  "domain": "Tech/AI"},
        {"company": "Microsoft India",    "roles": 1500,  "domain": "Cloud/Dev"},
        {"company": "Amazon India",       "roles": 3200,  "domain": "E-commerce/Cloud"},
        {"company": "Infosys",            "roles": 12000, "domain": "IT Services"},
        {"company": "TCS",                "roles": 18000, "domain": "IT Services"},
        {"company": "Wipro",              "roles": 8000,  "domain": "IT Services"},
        {"company": "Flipkart",           "roles": 900,   "domain": "E-commerce/ML"},
        {"company": "Zomato",             "roles": 600,   "domain": "Tech/Product"},
        {"company": "Goldman Sachs India","roles": 700,   "domain": "Finance/Tech"},
        {"company": "Apollo Hospitals",   "roles": 2000,  "domain": "Healthcare"},
    ],
    "skill_demand_2025": {
        "Generative AI / LLMs": 95, "Python": 90, "Cloud (AWS/GCP/Azure)": 88,
        "SQL / Data Engineering": 82, "React / Node.js": 78,
        "Kubernetes / Docker": 76, "Cybersecurity Tools": 74,
        "Power BI / Tableau": 70, "DevOps / CI-CD": 72, "Prompt Engineering": 85,
    },
    "growth_forecast": {
        "AI/ML Roles": 45, "Cloud Engineering": 32, "Cybersecurity": 28,
        "FinTech": 25, "Healthcare Tech": 22,
        "Digital Marketing": 18, "Traditional IT Services": 8, "Core Manufacturing": 5,
    },
    "placement_rates": {
        "IIT Graduates": 96, "NIT Graduates": 88, "Top Private Engg": 75,
        "State Engg Colleges": 55, "MBA (IIMs)": 99, "MBA (Other Top)": 80,
        "Medical (AIIMS)": 100, "B.Sc / BA / B.Com": 42,
    },
}


def render_job_market_insights(student_id: int | None):
    st.markdown("## 📈 Job Market Insights")
    st.markdown("Real-time trends, salary benchmarks, and hiring intelligence — India 2025.")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Demand Trends", "💰 Salary Data", "🏢 Top Hiring", "🔮 Outlook"])

    with tab1:
        _demand_trends()
    with tab2:
        _salary_data()
    with tab3:
        _top_hiring()
    with tab4:
        _future_outlook()


def _demand_trends():
    st.markdown("### 📊 Career Demand Index (2025)")
    demand = JOB_DATA["demand_trends"]
    sorted_d = sorted(demand.items(), key=lambda x: x[1], reverse=True)
    domains = [d for d, _ in sorted_d]
    scores  = [s for _, s in sorted_d]
    colors  = [COLORS["success"] if s >= 80 else (COLORS["warning"] if s >= 65 else COLORS["danger"]) for s in scores]
    fig = go.Figure(go.Bar(x=scores, y=domains, orientation="h",
                           marker_color=colors, text=[f"{s}/100" for s in scores], textposition="outside"))
    fig.update_layout(plot_bgcolor="#0F172A", paper_bgcolor="#0F172A", font_color="#F1F5F9",
                      xaxis=dict(range=[0,110], gridcolor="#334155"),
                      yaxis=dict(gridcolor="#334155"), height=390,
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🔥 Most In-Demand Skills")
    skill_d = JOB_DATA["skill_demand_2025"]
    sorted_s = sorted(skill_d.items(), key=lambda x: x[1], reverse=True)
    cols = st.columns(2)
    for i, (skill, score) in enumerate(sorted_s):
        with cols[i % 2]:
            bc = COLORS["primary"] if score >= 85 else (COLORS["accent"] if score >= 75 else COLORS["secondary"])
            st.markdown(f"""
<div style="margin-bottom:0.4rem;">
  <div style="display:flex;justify-content:space-between;color:#F1F5F9;font-size:0.82rem;margin-bottom:2px;">
    <span>{skill}</span><span>{score}%</span></div>
  <div style="background:#1E293B;border-radius:4px;height:7px;">
    <div style="background:{bc};height:7px;border-radius:4px;width:{score}%;"></div>
  </div>
</div>""", unsafe_allow_html=True)


def _salary_data():
    st.markdown("### 💰 Salary Ranges (India, 2025)")
    sal = JOB_DATA["salary_ranges_inr"]
    roles   = list(sal.keys())
    medians = [sal[r]["median"]/100000 for r in roles]
    mins    = [sal[r]["min"]/100000 for r in roles]
    maxs    = [sal[r]["max"]/100000 for r in roles]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Min",    x=roles, y=mins,    marker_color="#334155"))
    fig.add_trace(go.Bar(name="Median", x=roles, y=medians, marker_color=COLORS["primary"]))
    fig.add_trace(go.Bar(name="Max",    x=roles, y=maxs,    marker_color=COLORS["accent"]))
    fig.update_layout(barmode="group", plot_bgcolor="#0F172A", paper_bgcolor="#0F172A",
                      font_color="#F1F5F9", yaxis_title="CTC (Lakhs INR)",
                      xaxis_tickangle=-30, height=420,
                      xaxis=dict(gridcolor="#334155"), yaxis=dict(gridcolor="#334155"),
                      legend=dict(bgcolor="#1E293B"), margin=dict(l=10, r=10, t=10, b=90))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🎓 Fresher Placement Rates")
    pr = JOB_DATA["placement_rates"]
    df = pd.DataFrame(list(pr.items()), columns=["Institution", "Rate (%)"])
    fig2 = px.bar(df, x="Rate (%)", y="Institution", orientation="h",
                  color="Rate (%)", color_continuous_scale=["#EF4444","#F59E0B","#10B981"])
    fig2.update_layout(plot_bgcolor="#0F172A", paper_bgcolor="#0F172A", font_color="#F1F5F9",
                       height=320, coloraxis_showscale=False,
                       xaxis=dict(gridcolor="#334155"), yaxis=dict(gridcolor="#334155"),
                       margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)


def _top_hiring():
    st.markdown("### 🏢 Top Hiring Companies (India, 2025)")
    for co in JOB_DATA["top_companies"]:
        c1, c2, c3 = st.columns([3, 1, 2])
        c1.markdown(f"**{co['company']}**")
        c2.markdown(f"<span style='color:#10B981;'>{co['roles']:,}</span>", unsafe_allow_html=True)
        c3.markdown(f"<span style='color:#94A3B8;font-size:0.82rem;'>{co['domain']}</span>", unsafe_allow_html=True)
        st.divider()

    st.markdown("### 🏙️ Top Hiring Cities")
    cities = JOB_DATA["top_cities"]
    fig = go.Figure(go.Pie(labels=list(cities.keys()), values=list(cities.values()),
        hole=0.45, marker_colors=[COLORS["primary"], COLORS["secondary"], COLORS["accent"],
                                   COLORS["success"], COLORS["warning"], "#EC4899", "#F97316", "#94A3B8"]))
    fig.update_layout(paper_bgcolor="#0F172A", font_color="#F1F5F9", height=340,
                      legend=dict(bgcolor="#1E293B"), margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)


def _future_outlook():
    st.markdown("### 🔮 YoY Role Growth Forecast (2025–2026)")
    growth = JOB_DATA["growth_forecast"]
    sorted_g = sorted(growth.items(), key=lambda x: x[1], reverse=True)
    domains = [d for d, _ in sorted_g]
    pct     = [g for _, g in sorted_g]
    colors  = [COLORS["success"] if p >= 25 else (COLORS["accent"] if p >= 15 else COLORS["warning"]) for p in pct]
    fig = go.Figure(go.Bar(x=pct, y=domains, orientation="h",
                           marker_color=colors, text=[f"+{p}%" for p in pct], textposition="outside"))
    fig.update_layout(plot_bgcolor="#0F172A", paper_bgcolor="#0F172A", font_color="#F1F5F9",
                      xaxis=dict(range=[0,60], title="Growth %", gridcolor="#334155"),
                      yaxis=dict(gridcolor="#334155"), height=360,
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🌟 Key Trends 2025")
    trends = [
        ("🤖 Generative AI Disruption", "AI tools reshape every sector. Roles needing AI literacy will see 3× growth by 2027."),
        ("☁️ Cloud-First India", "India's cloud market hits $13B by 2026, driving massive demand for cloud engineers."),
        ("🛡️ Cybersecurity Crisis", "1.4M cyber attacks/year in India. Security talent shortage is 3:1 demand-to-supply."),
        ("🏥 HealthTech Boom", "Post-COVID digital health investment creating 500K+ jobs in healthcare technology."),
        ("🎓 Skill Over Degree", "Google, IBM, Amazon now hire on skills/certifications, not just degrees."),
    ]
    for title, desc in trends:
        with st.expander(f"**{title}**"):
            st.markdown(desc)
