# src/pages/settings.py
# CareerMitra AI Assistant – Settings Page

import streamlit as st
import os
from src.config import (
    APP_NAME, APP_VERSION, IBM_WATSONX_URL, IBM_WATSONX_PROJECT_ID,
    GRANITE_MODEL_ID, GRANITE_PARAMS, ibm_configured, COLORS,
)
from src.ibm_granite import get_model_error, _client_cache


def render_settings():
    st.markdown("## ⚙️ Settings")
    st.markdown("Configure your CareerMitra AI Assistant experience.")

    tab1, tab2, tab3 = st.tabs(["🔧 IBM watsonx.ai", "🎨 About", "🗄️ Data Management"])

    with tab1:
        _ibm_settings()
    with tab2:
        _about_section()
    with tab3:
        _data_management()


def _ibm_settings():
    st.markdown("### 🔧 IBM watsonx.ai Configuration")

    ibm_ok = ibm_configured()
    model_error = get_model_error()

    # Connection status card
    if ibm_ok and not model_error:
        status_bg    = "rgba(16,185,129,0.1)"
        status_border = "rgba(16,185,129,0.4)"
        status_icon  = "✅"
        status_title = "IBM Granite Connected"
        status_sub   = "Your AI features are fully active."
        status_color = "#10B981"
    elif ibm_ok and model_error:
        status_bg    = "rgba(239,68,68,0.1)"
        status_border = "rgba(239,68,68,0.4)"
        status_icon  = "⚠️"
        status_title = "Configuration Error"
        status_sub   = "Credentials set but connection failed."
        status_color = "#EF4444"
    else:
        status_bg    = "rgba(245,158,11,0.1)"
        status_border = "rgba(245,158,11,0.35)"
        status_icon  = "⚡"
        status_title = "Demo Mode"
        status_sub   = "Add credentials to enable AI features."
        status_color = "#F59E0B"

    st.markdown(f"""
<div style="background:{status_bg};border:1px solid {status_border};
            border-radius:12px;padding:1rem 1.2rem;margin-bottom:1.2rem;">
    <div style="display:flex;align-items:center;gap:0.75rem;">
        <span style="font-size:1.5rem;">{status_icon}</span>
        <div>
            <div style="color:{status_color};font-weight:700;font-size:0.95rem;">{status_title}</div>
            <div style="color:#94A3B8;font-size:0.82rem;">{status_sub}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    if model_error and ibm_ok:
        with st.expander("⚠️ View Error Details", expanded=True):
            st.markdown(model_error)

    # Current config (no API key exposure)
    st.markdown("#### Current Configuration")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:10px;padding:1rem;">
    <div style="color:#94A3B8;font-size:0.72rem;font-weight:600;letter-spacing:0.5px;margin-bottom:0.6rem;">ENDPOINT</div>
    <div style="color:#E2E8F0;font-size:0.88rem;word-break:break-all;">{IBM_WATSONX_URL or "Not set"}</div>
    <div style="color:#94A3B8;font-size:0.72rem;margin-top:0.5rem;">Model: {GRANITE_MODEL_ID or "Not set"}</div>
</div>
""", unsafe_allow_html=True)
    with col2:
        project_display = (IBM_WATSONX_PROJECT_ID[:8] + "..." + IBM_WATSONX_PROJECT_ID[-4:]
                           if IBM_WATSONX_PROJECT_ID and len(IBM_WATSONX_PROJECT_ID) > 12
                           else IBM_WATSONX_PROJECT_ID or "Not set")
        st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:10px;padding:1rem;">
    <div style="color:#94A3B8;font-size:0.72rem;font-weight:600;letter-spacing:0.5px;margin-bottom:0.6rem;">PROJECT</div>
    <div style="color:#E2E8F0;font-size:0.88rem;">{project_display}</div>
    <div style="color:#94A3B8;font-size:0.72rem;margin-top:0.5rem;">
        API Key: {"✅ Set" if os.getenv("IBM_WATSONX_API_KEY") else "❌ Not set"}
    </div>
</div>
""", unsafe_allow_html=True)

    # Model parameters
    st.markdown("#### Granite Model Parameters")
    p1, p2, p3 = st.columns(3)
    params = [
        ("Max New Tokens", GRANITE_PARAMS.get("max_new_tokens", 800)),
        ("Temperature",    GRANITE_PARAMS.get("temperature", 0.7)),
        ("Top-P",          GRANITE_PARAMS.get("top_p", 0.9)),
    ]
    for col, (label, val) in zip([p1, p2, p3], params):
        with col:
            st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:8px;padding:0.8rem;text-align:center;">
    <div style="color:#4F46E5;font-size:1.2rem;font-weight:700;">{val}</div>
    <div style="color:#94A3B8;font-size:0.72rem;">{label}</div>
</div>
""", unsafe_allow_html=True)

    # Setup guide
    st.markdown("---")
    with st.expander("📖 How to Configure IBM watsonx.ai", expanded=not ibm_ok):
        st.markdown("""
**Step-by-step setup:**

1. **Create IBM Cloud account** → [cloud.ibm.com](https://cloud.ibm.com)
2. **Create a watsonx.ai project** at [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com) in the **Sydney (au-syd)** region
3. **Get your Project ID** → Project → Settings → General → Project ID
4. **Generate API Key** → IBM Cloud → Manage → Access (IAM) → API Keys → Create
5. **Edit your `.env` file** in the project root:
```env
IBM_WATSONX_API_KEY=your_api_key_here
IBM_WATSONX_PROJECT_ID=your_project_id_here
IBM_WATSONX_URL=https://au-syd.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-13b-instruct-v2
```
6. **Restart the app**: `python -m streamlit run app.py`

> 🔒 **Security:** API keys are read from the `.env` file and never displayed in the UI. Never commit your `.env` file to Git.

**Supported IBM Granite Models:**
| Model ID | Description |
|---|---|
| `ibm/granite-13b-instruct-v2` | Best for career guidance (recommended) |
| `ibm/granite-20b-multilingual` | Multilingual — for Hindi/Hinglish support |
""")

    # Test connection button
    st.markdown("---")
    if st.button("🔌 Test IBM Granite Connection", use_container_width=True):
        if not ibm_configured():
            st.error("⚠️ IBM credentials not configured. Edit your `.env` file and restart the app.")
        else:
            with st.spinner("Testing connection to IBM watsonx.ai..."):
                # Clear cache so we get a fresh connection test
                _client_cache.clear()
                from src.ibm_granite import _get_model
                model = _get_model()
            if model is not None:
                st.success("✅ IBM Granite connected successfully!")
            else:
                err = get_model_error() or "Unknown error"
                st.error(f"❌ Connection failed: {err}")


def _about_section():
    st.markdown("### 🎓 About CareerMitra AI Assistant")
    st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(79,70,229,0.1),rgba(6,182,212,0.05));
            border:1px solid rgba(79,70,229,0.25);border-radius:16px;padding:1.5rem;
            margin-bottom:1.2rem;">
    <div style="text-align:center;margin-bottom:1.2rem;">
        <div style="font-size:3rem;">🎓</div>
        <div style="color:#E2E8F0;font-size:1.4rem;font-weight:800;margin:0.4rem 0;">{APP_NAME}</div>
        <div style="color:#94A3B8;font-size:0.85rem;">Your Intelligent AI Career Companion</div>
        <div style="color:#4F46E5;font-size:0.78rem;margin-top:0.3rem;">v{APP_VERSION}</div>
    </div>
    <div style="color:#94A3B8;font-size:0.88rem;line-height:1.7;text-align:center;max-width:550px;margin:0 auto;">
        CareerMitra AI Assistant is an intelligent, IBM Granite-powered career guidance platform
        designed to help students discover their ideal career path, bridge skill gaps,
        and build a clear roadmap to career success.
    </div>
</div>
""", unsafe_allow_html=True)

    # Feature list
    st.markdown("#### 🌟 Platform Features")
    features = [
        ("🏠", "Home Dashboard",         "Premium AI dashboard with career stats and navigation"),
        ("👤", "Student Profile",         "Complete career profile with skills, interests, and goals"),
        ("🤖", "AI Career Counselor",     "IBM Granite-powered live chat for personalised career advice"),
        ("🎯", "Career Recommendations",  "AI-matched career paths with compatibility scores and growth data"),
        ("📊", "Skill Gap Analysis",      "Radar chart and AI analysis of your skill gaps"),
        ("🗺️", "Career Roadmap",          "Phase-by-phase personalised career milestone plan"),
        ("📈", "Job Market Insights",     "Salary benchmarks, demand trends, top hiring companies"),
        ("📄", "Resume Analyzer",         "AI-powered resume feedback, ATS optimisation, keyword gaps"),
        ("🎤", "AI Interview Prep",       "Domain-specific questions with AI model answers and mock interviews"),
        ("📋", "Progress Dashboard",      "Milestone tracker and career progress visualisation"),
    ]
    cols = st.columns(2)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:8px;
            padding:0.65rem 0.9rem;margin-bottom:0.4rem;display:flex;gap:0.6rem;align-items:flex-start;">
    <span style="font-size:1.1rem;">{icon}</span>
    <div>
        <div style="color:#E2E8F0;font-weight:600;font-size:0.84rem;">{title}</div>
        <div style="color:#94A3B8;font-size:0.75rem;line-height:1.4;">{desc}</div>
    </div>
</div>
""", unsafe_allow_html=True)

    # Tech stack
    st.markdown("---")
    st.markdown("#### 🛠️ Technology Stack")
    tech_cols = st.columns(4)
    stack = [
        ("🧠", "IBM Granite 13B", "LLM via watsonx.ai", "#4F46E5"),
        ("🐍", "Python 3.11+",    "Core language",       "#10B981"),
        ("📊", "Streamlit",       "Web UI framework",    "#EF4444"),
        ("🗄️", "SQLite",          "Local database",      "#06B6D4"),
    ]
    for col, (icon, name, desc, color) in zip(tech_cols, stack):
        with col:
            st.markdown(f"""
<div style="background:#1E293B;border:1px solid {color}44;border-radius:10px;
            padding:0.9rem;text-align:center;">
    <div style="font-size:1.6rem;">{icon}</div>
    <div style="color:{color};font-weight:700;font-size:0.88rem;margin:0.3rem 0;">{name}</div>
    <div style="color:#94A3B8;font-size:0.72rem;">{desc}</div>
</div>
""", unsafe_allow_html=True)


def _data_management():
    st.markdown("### 🗄️ Data Management")

    from src.database import get_all_students, init_db
    students = get_all_students()

    st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:10px;
            padding:1rem;margin-bottom:1rem;display:flex;justify-content:space-between;align-items:center;">
    <div>
        <div style="color:#E2E8F0;font-weight:600;">Database Status</div>
        <div style="color:#94A3B8;font-size:0.82rem;">{len(students)} student profile(s) stored</div>
    </div>
    <div style="color:#10B981;font-size:1.3rem;">✅</div>
</div>
""", unsafe_allow_html=True)

    if students:
        st.markdown("#### 👥 Registered Profiles")
        for s in students:
            st.markdown(f"""
<div style="background:#0A0F1E;border:1px solid #334155;border-radius:8px;
            padding:0.55rem 0.9rem;margin-bottom:0.3rem;
            display:flex;justify-content:space-between;align-items:center;">
    <div>
        <span style="color:#E2E8F0;font-weight:600;font-size:0.88rem;">{s.get('name','—')}</span>
        <span style="color:#94A3B8;font-size:0.78rem;margin-left:0.75rem;">{s.get('email','—')}</span>
    </div>
    <div style="color:#94A3B8;font-size:0.72rem;">{s.get('education','—')} · {s.get('city','—')}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("⚠️ Database Operations"):
        st.warning("These operations cannot be undone.")
        if st.button("🔄 Re-initialise Database (safe)", use_container_width=True):
            init_db()
            st.success("✅ Database tables verified/created.")

        st.markdown("**Clear all data** — removes all student profiles, chat history, and milestones.")
        confirm = st.text_input("Type `DELETE ALL` to confirm:", key="confirm_delete")
        if st.button("🗑️ Clear All Data", use_container_width=True):
            if confirm == "DELETE ALL":
                import os, shutil
                db_path = os.path.join("data", "careermitra.db")
                if os.path.exists(db_path):
                    os.remove(db_path)
                init_db()
                st.session_state["student_id"] = None
                st.session_state["chat_messages"] = []
                st.success("✅ All data cleared. Database re-initialised.")
                st.rerun()
            else:
                st.error("Please type `DELETE ALL` to confirm.")
