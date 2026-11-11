# app.py
# CareerMitra AI Assistant – Main Streamlit Application Entry Point
# IBM Granite via watsonx.ai Edition  |  v2.0.0

import os
import sys
import streamlit as st

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import APP_NAME, APP_SUBTITLE, APP_TAGLINE, APP_ICON, PAGES, ibm_configured
from src.database import init_db

# Page modules
from src.pages.home                    import render_home
from src.pages.student_profile         import render_student_profile
from src.pages.ai_counselor            import render_ai_counselor
from src.pages.career_recommendations  import render_career_recommendations
from src.pages.skill_gap               import render_skill_gap_analysis
from src.pages.roadmap                 import render_career_roadmap
from src.pages.job_market              import render_job_market_insights
from src.pages.dashboard               import render_dashboard
from src.pages.resume_analyzer         import render_resume_analyzer
from src.pages.interview_prep          import render_interview_prep
from src.pages.settings                import render_settings

# ── Streamlit page configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Database initialisation ───────────────────────────────────────────────────
init_db()

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
html, body, [class*="css"] {
    background-color: #0A0F1E !important;
    color: #E2E8F0 !important;
    font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #0A0F1E 100%) !important;
    border-right: 1px solid rgba(79,70,229,0.25);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    color: white !important;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 0.5rem 1.1rem;
    transition: all 0.2s ease;
    box-shadow: 0 2px 12px rgba(79,70,229,0.35);
}
.stButton > button:hover {
    opacity: 0.90;
    box-shadow: 0 4px 20px rgba(79,70,229,0.55);
    transform: translateY(-1px);
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea,
.stSelectbox > div > div {
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    color: #E2E8F0 !important;
    border-radius: 10px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: #4F46E5 !important;
    box-shadow: 0 0 0 2px rgba(79,70,229,0.2) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #1E293B;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #334155;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #94A3B8;
    border-radius: 8px;
    font-weight: 500;
    padding: 0.4rem 1rem;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4F46E5, #7C3AED) !important;
    color: white !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    margin-bottom: 0.6rem;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #1E293B;
    border-radius: 12px;
    padding: 0.75rem;
    border: 1px solid #334155;
}

/* ── Misc ── */
hr { border-color: #1E293B !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0A0F1E; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4F46E5; }
.block-container { padding-top: 1.5rem !important; max-width: 1200px; }
#MainMenu { visibility: hidden; }
footer   { visibility: hidden; }
header   { visibility: hidden; }

/* ── Nav button active glow ── */
.nav-active .stButton > button {
    background: linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%) !important;
    box-shadow: 0 0 18px rgba(79,70,229,0.6) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "current_page"   not in st.session_state: st.session_state["current_page"]   = "home"
if "student_id"     not in st.session_state: st.session_state["student_id"]     = None
if "chat_messages"  not in st.session_state: st.session_state["chat_messages"]  = []

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # ── Branding header ──────────────────────────────────────────────────────
    ibm_ok    = ibm_configured()
    badge_clr = "#10B981" if ibm_ok else "#F59E0B"
    badge_txt = "IBM Granite ✓" if ibm_ok else "Demo Mode"

    st.markdown(f"""
<div style="
    background: linear-gradient(135deg, rgba(79,70,229,0.15) 0%, rgba(6,182,212,0.08) 100%);
    border-bottom: 1px solid rgba(79,70,229,0.3);
    padding: 1.4rem 1rem 1rem 1rem;
    margin: -1rem -1rem 0.6rem -1rem;
    text-align: center;
">
    <div style="
        width:62px; height:62px; margin:0 auto 0.6rem auto;
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        border-radius: 18px;
        display:flex; align-items:center; justify-content:center;
        font-size:2rem; box-shadow: 0 4px 20px rgba(79,70,229,0.5);
    ">🎓</div>
    <div style="color:#E2E8F0; font-size:1.05rem; font-weight:700; letter-spacing:-0.3px;">{APP_NAME}</div>
    <div style="color:#94A3B8; font-size:0.72rem; margin:0.18rem 0 0.5rem 0;">{APP_SUBTITLE}</div>
    <div style="
        display:inline-block;
        background:{badge_clr}1A; color:{badge_clr};
        border:1px solid {badge_clr}44;
        border-radius:20px; padding:0.15rem 0.65rem;
        font-size:0.68rem; font-weight:600;
    ">⚡ {badge_txt}</div>
</div>
""", unsafe_allow_html=True)

    # ── Active student card ───────────────────────────────────────────────────
    student_id = st.session_state.get("student_id")
    if student_id:
        from src.database import get_student_by_id as _gsid
        s = _gsid(student_id)
        if s:
            st.markdown(f"""
<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.3);
            border-radius:10px;padding:0.6rem 0.85rem;margin-bottom:0.7rem;">
    <div style="color:#10B981;font-size:0.68rem;font-weight:600;letter-spacing:0.5px;">✅ ACTIVE SESSION</div>
    <div style="color:#E2E8F0;font-weight:700;font-size:0.92rem;margin-top:0.15rem;">{s['name']}</div>
    <div style="color:#94A3B8;font-size:0.72rem;">{s.get('education','—')} · {s.get('city','—')}</div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="background:rgba(79,70,229,0.07);border:1px dashed rgba(79,70,229,0.35);
            border-radius:10px;padding:0.6rem 0.85rem;margin-bottom:0.7rem;">
    <div style="color:#94A3B8;font-size:0.8rem;">👋 No profile active</div>
    <div style="color:#7C3AED;font-size:0.78rem;font-weight:600;">→ Start with Student Profile</div>
</div>""", unsafe_allow_html=True)

    # ── Navigation ────────────────────────────────────────────────────────────
    st.markdown("<div style='color:#475569;font-size:0.68rem;font-weight:700;letter-spacing:1px;padding:0.2rem 0 0.4rem 0;'>NAVIGATION</div>", unsafe_allow_html=True)

    current = st.session_state.get("current_page", "home")
    for page in PAGES:
        is_active = current == page["key"]
        btn_style = ""
        if is_active:
            st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(79,70,229,0.3),rgba(6,182,212,0.15));
            border:1px solid rgba(79,70,229,0.5);border-radius:10px;
            padding:0.5rem 0.85rem;margin-bottom:3px;
            box-shadow:0 0 12px rgba(79,70,229,0.25);">
    <span style="color:#E2E8F0;font-weight:700;font-size:0.88rem;">{page['name']}</span>
</div>""", unsafe_allow_html=True)
        else:
            if st.button(page["name"], key=f"nav_{page['key']}", use_container_width=True):
                st.session_state["current_page"] = page["key"]
                st.rerun()

    st.markdown("<div style='border-top:1px solid #1E293B;margin:0.7rem 0 0.6rem 0;'></div>", unsafe_allow_html=True)

    # ── Load profile ─────────────────────────────────────────────────────────
    with st.expander("🔑 Load Existing Profile"):
        email_input = st.text_input("Email:", key="lookup_email", placeholder="student@email.com")
        if st.button("Load Profile", key="load_btn", use_container_width=True):
            if email_input:
                from src.database import get_student_by_email as _gsbe
                found = _gsbe(email_input)
                if found:
                    st.session_state["student_id"]    = found["id"]
                    st.session_state["chat_messages"] = []
                    st.success(f"✅ Loaded: {found['name']}")
                    st.rerun()
                else:
                    st.error("No profile found.")
            else:
                st.warning("Enter an email address.")

    if student_id:
        if st.button("🚪 Clear Session", use_container_width=True):
            st.session_state["student_id"]    = None
            st.session_state["chat_messages"] = []
            st.session_state["current_page"]  = "home"
            st.rerun()

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""
<div style="text-align:center;color:#334155;font-size:0.64rem;padding-top:0.75rem;
            border-top:1px solid #1E293B;margin-top:0.5rem;">
    CareerMitra AI Assistant v2.0.0<br>
    <span style="color:#4F46E5;">IBM Granite</span> · Streamlit · SQLite
</div>""", unsafe_allow_html=True)


# ── Page routing ──────────────────────────────────────────────────────────────
page       = st.session_state.get("current_page", "home")
student_id = st.session_state.get("student_id")

if page == "home":
    render_home()
elif page == "profile":
    new_id = render_student_profile(student_id)
    if new_id:
        st.session_state["student_id"] = new_id
elif page == "counselor":
    render_ai_counselor(student_id)
elif page == "recommendations":
    render_career_recommendations(student_id)
elif page == "skill_gap":
    render_skill_gap_analysis(student_id)
elif page == "roadmap":
    render_career_roadmap(student_id)
elif page == "job_market":
    render_job_market_insights(student_id)
elif page == "resume":
    render_resume_analyzer(student_id)
elif page == "interview":
    render_interview_prep(student_id)
elif page == "dashboard":
    render_dashboard(student_id)
elif page == "settings":
    render_settings()
