# src/pages/home.py
# CareerMitra AI Assistant – Home / Landing Page (Premium AI Dashboard)

import streamlit as st
from src.config import APP_NAME, APP_SUBTITLE, APP_TAGLINE, COLORS, ibm_configured

# ── SVG Illustrations (inline, no external dependencies) ─────────────────────

_SVG_HERO = """
<svg viewBox="0 0 400 280" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:400px;">
  <defs>
    <radialGradient id="glow1" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#4F46E5" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#4F46E5" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow2" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#06B6D4" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#06B6D4" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <!-- Background glow -->
  <ellipse cx="200" cy="140" rx="180" ry="120" fill="url(#glow1)"/>
  <ellipse cx="280" cy="80" rx="100" ry="70" fill="url(#glow2)"/>
  <!-- Neural network nodes -->
  <!-- Layer 1 -->
  <circle cx="60" cy="100" r="10" fill="#4F46E5" opacity="0.9"/>
  <circle cx="60" cy="140" r="10" fill="#4F46E5" opacity="0.9"/>
  <circle cx="60" cy="180" r="10" fill="#4F46E5" opacity="0.9"/>
  <!-- Layer 2 -->
  <circle cx="140" cy="80" r="12" fill="#7C3AED" opacity="0.9"/>
  <circle cx="140" cy="120" r="12" fill="#7C3AED" opacity="0.9"/>
  <circle cx="140" cy="160" r="12" fill="#7C3AED" opacity="0.9"/>
  <circle cx="140" cy="200" r="12" fill="#7C3AED" opacity="0.9"/>
  <!-- Layer 3 (center - AI brain) -->
  <circle cx="220" cy="140" r="30" fill="none" stroke="#4F46E5" stroke-width="2" opacity="0.6"/>
  <circle cx="220" cy="140" r="22" fill="none" stroke="#7C3AED" stroke-width="1.5" opacity="0.5"/>
  <circle cx="220" cy="140" r="14" fill="#4F46E5" opacity="0.85"/>
  <text x="220" y="145" text-anchor="middle" fill="white" font-size="12" font-weight="bold">AI</text>
  <!-- Layer 4 -->
  <circle cx="300" cy="80" r="12" fill="#06B6D4" opacity="0.9"/>
  <circle cx="300" cy="120" r="12" fill="#06B6D4" opacity="0.9"/>
  <circle cx="300" cy="160" r="12" fill="#06B6D4" opacity="0.9"/>
  <circle cx="300" cy="200" r="12" fill="#06B6D4" opacity="0.9"/>
  <!-- Layer 5 -->
  <circle cx="375" cy="100" r="10" fill="#10B981" opacity="0.9"/>
  <circle cx="375" cy="140" r="10" fill="#10B981" opacity="0.9"/>
  <circle cx="375" cy="180" r="10" fill="#10B981" opacity="0.9"/>
  <!-- Connections L1→L2 -->
  <line x1="70" y1="100" x2="128" y2="80"  stroke="#4F46E5" stroke-width="1" opacity="0.4"/>
  <line x1="70" y1="100" x2="128" y2="120" stroke="#4F46E5" stroke-width="1" opacity="0.4"/>
  <line x1="70" y1="140" x2="128" y2="120" stroke="#4F46E5" stroke-width="1" opacity="0.4"/>
  <line x1="70" y1="140" x2="128" y2="160" stroke="#4F46E5" stroke-width="1" opacity="0.4"/>
  <line x1="70" y1="180" x2="128" y2="160" stroke="#4F46E5" stroke-width="1" opacity="0.4"/>
  <line x1="70" y1="180" x2="128" y2="200" stroke="#4F46E5" stroke-width="1" opacity="0.4"/>
  <!-- Connections L2→L3 -->
  <line x1="152" y1="80"  x2="190" y2="140" stroke="#7C3AED" stroke-width="1.2" opacity="0.5"/>
  <line x1="152" y1="120" x2="190" y2="140" stroke="#7C3AED" stroke-width="1.2" opacity="0.5"/>
  <line x1="152" y1="160" x2="190" y2="140" stroke="#7C3AED" stroke-width="1.2" opacity="0.5"/>
  <line x1="152" y1="200" x2="190" y2="140" stroke="#7C3AED" stroke-width="1.2" opacity="0.5"/>
  <!-- Connections L3→L4 -->
  <line x1="250" y1="140" x2="288" y2="80"  stroke="#06B6D4" stroke-width="1.2" opacity="0.5"/>
  <line x1="250" y1="140" x2="288" y2="120" stroke="#06B6D4" stroke-width="1.2" opacity="0.5"/>
  <line x1="250" y1="140" x2="288" y2="160" stroke="#06B6D4" stroke-width="1.2" opacity="0.5"/>
  <line x1="250" y1="140" x2="288" y2="200" stroke="#06B6D4" stroke-width="1.2" opacity="0.5"/>
  <!-- Connections L4→L5 -->
  <line x1="312" y1="80"  x2="365" y2="100" stroke="#10B981" stroke-width="1" opacity="0.4"/>
  <line x1="312" y1="120" x2="365" y2="100" stroke="#10B981" stroke-width="1" opacity="0.4"/>
  <line x1="312" y1="120" x2="365" y2="140" stroke="#10B981" stroke-width="1" opacity="0.4"/>
  <line x1="312" y1="160" x2="365" y2="140" stroke="#10B981" stroke-width="1" opacity="0.4"/>
  <line x1="312" y1="160" x2="365" y2="180" stroke="#10B981" stroke-width="1" opacity="0.4"/>
  <line x1="312" y1="200" x2="365" y2="180" stroke="#10B981" stroke-width="1" opacity="0.4"/>
  <!-- Floating data points -->
  <circle cx="100" cy="240" r="3" fill="#F59E0B" opacity="0.7"/>
  <circle cx="180" cy="250" r="4" fill="#EF4444" opacity="0.6"/>
  <circle cx="260" cy="245" r="3" fill="#10B981" opacity="0.7"/>
  <circle cx="340" cy="238" r="4" fill="#7C3AED" opacity="0.6"/>
</svg>
"""

_SVG_CAREER = """
<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg" style="width:56px;height:56px;">
  <rect width="80" height="80" rx="20" fill="url(#cg{idx})"/>
  <defs>
    <linearGradient id="cg{idx}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <text x="40" y="52" text-anchor="middle" font-size="32">{icon}</text>
</svg>
"""


def _icon_card(idx, icon, c1, c2):
    return _SVG_CAREER.replace("{idx}", str(idx)).replace("{c1}", c1).replace("{c2}", c2).replace("{icon}", icon)


def render_home():
    # ── Hero Section ──────────────────────────────────────────────────────────
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        ibm_ok = ibm_configured()
        status_badge = (
            '<span style="background:rgba(16,185,129,0.15);color:#10B981;border:1px solid rgba(16,185,129,0.4);'
            'border-radius:20px;padding:0.2rem 0.75rem;font-size:0.75rem;font-weight:600;">⚡ IBM Granite Connected</span>'
            if ibm_ok else
            '<span style="background:rgba(245,158,11,0.12);color:#F59E0B;border:1px solid rgba(245,158,11,0.35);'
            'border-radius:20px;padding:0.2rem 0.75rem;font-size:0.75rem;font-weight:600;">⚡ Demo Mode</span>'
        )
        st.markdown(f"""
<div style="padding: 2.5rem 0 1.5rem 0;">
    {status_badge}
    <h1 style="
        color:#E2E8F0;
        font-size:2.9rem;
        font-weight:800;
        line-height:1.15;
        margin:0.7rem 0 0.3rem 0;
        letter-spacing:-1px;
    ">
        CareerMitra<br>
        <span style="background:linear-gradient(135deg,#4F46E5,#06B6D4);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                     background-clip:text;">AI Assistant</span>
    </h1>
    <p style="color:#94A3B8;font-size:1.05rem;line-height:1.7;margin:0.6rem 0 0 0;max-width:480px;">
        Discover your strengths, explore career opportunities, identify skill gaps, and build a
        personalised roadmap to achieve your dream career with the power of Artificial Intelligence.
    </p>
</div>
""", unsafe_allow_html=True)

        # CTA Buttons
        btn1, btn2, btn3 = st.columns(3, gap="small")
        with btn1:
            if st.button("🚀 Start Assessment", use_container_width=True, key="cta_profile"):
                st.session_state["current_page"] = "profile"
                st.rerun()
        with btn2:
            if st.button("🎯 Explore Careers", use_container_width=True, key="cta_rec"):
                st.session_state["current_page"] = "recommendations"
                st.rerun()
        with btn3:
            if st.button("🤖 Chat with AI", use_container_width=True, key="cta_chat"):
                st.session_state["current_page"] = "counselor"
                st.rerun()

    with col_right:
        st.markdown(f"""
<div style="padding:1.5rem 0; display:flex; justify-content:center; align-items:center;">
    {_SVG_HERO}
</div>
""", unsafe_allow_html=True)

    # ── Stats Row ─────────────────────────────────────────────────────────────
    st.markdown("""
<div style="background:linear-gradient(135deg,rgba(79,70,229,0.1),rgba(6,182,212,0.05));
            border:1px solid rgba(79,70,229,0.2);border-radius:16px;padding:1.2rem;
            margin:0.5rem 0 1.5rem 0;">
    <div style="display:flex;justify-content:space-around;flex-wrap:wrap;gap:1rem;text-align:center;">
        <div>
            <div style="font-size:1.8rem;font-weight:800;color:#4F46E5;">10+</div>
            <div style="color:#94A3B8;font-size:0.8rem;">Career Domains</div>
        </div>
        <div style="border-left:1px solid #1E293B;"></div>
        <div>
            <div style="font-size:1.8rem;font-weight:800;color:#06B6D4;">50+</div>
            <div style="color:#94A3B8;font-size:0.8rem;">Skills Tracked</div>
        </div>
        <div style="border-left:1px solid #1E293B;"></div>
        <div>
            <div style="font-size:1.8rem;font-weight:800;color:#7C3AED;">100+</div>
            <div style="color:#94A3B8;font-size:0.8rem;">Learning Resources</div>
        </div>
        <div style="border-left:1px solid #1E293B;"></div>
        <div>
            <div style="font-size:1.8rem;font-weight:800;color:#10B981;">24/7</div>
            <div style="color:#94A3B8;font-size:0.8rem;">AI Guidance</div>
        </div>
        <div style="border-left:1px solid #1E293B;"></div>
        <div>
            <div style="font-size:1.8rem;font-weight:800;color:#F59E0B;">8</div>
            <div style="color:#94A3B8;font-size:0.8rem;">AI Features</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── Feature Cards ─────────────────────────────────────────────────────────
    st.markdown("### 🌟 Platform Features")

    features = [
        {
            "key": "profile",
            "icon": "👤",
            "c1": "#4F46E5", "c2": "#7C3AED",
            "title": "Student Profile",
            "desc": "Build your complete career profile — education, skills, interests, and career goals in one place.",
            "btn": "Build Profile",
        },
        {
            "key": "counselor",
            "icon": "🤖",
            "c1": "#7C3AED", "c2": "#EC4899",
            "title": "AI Career Counselor",
            "desc": "Chat live with IBM Granite AI for personalised, context-aware career advice in English, Hindi, or Hinglish.",
            "btn": "Start Chatting",
        },
        {
            "key": "recommendations",
            "icon": "🎯",
            "c1": "#06B6D4", "c2": "#3B82F6",
            "title": "Career Recommendations",
            "desc": "AI-matched career paths scored against your unique profile with salary ranges and growth projections.",
            "btn": "Get Matched",
        },
        {
            "key": "skill_gap",
            "icon": "📊",
            "c1": "#10B981", "c2": "#06B6D4",
            "title": "Skill Gap Analysis",
            "desc": "Identify exactly which skills you need for your target role, with a radar chart and learning resources.",
            "btn": "Analyse Gaps",
        },
        {
            "key": "roadmap",
            "icon": "🗺️",
            "c1": "#F59E0B", "c2": "#EF4444",
            "title": "Career Roadmap",
            "desc": "Milestone-by-milestone personalised career plan generated by IBM Granite for your specific goal.",
            "btn": "Plan Journey",
        },
        {
            "key": "job_market",
            "icon": "📈",
            "c1": "#EF4444", "c2": "#F59E0B",
            "title": "Job Market Insights",
            "desc": "Salary benchmarks, demand trends, top hiring companies, and growth forecasts for India 2025.",
            "btn": "View Insights",
        },
        {
            "key": "resume",
            "icon": "📄",
            "c1": "#8B5CF6", "c2": "#4F46E5",
            "title": "Resume Analyzer",
            "desc": "Paste your resume and get AI-powered feedback on structure, keywords, ATS compatibility, and improvements.",
            "btn": "Analyse Resume",
        },
        {
            "key": "interview",
            "icon": "🎤",
            "c1": "#EC4899", "c2": "#8B5CF6",
            "title": "AI Interview Prep",
            "desc": "Practice domain-specific interview questions, get model answers, and build confidence before your interview.",
            "btn": "Prepare Now",
        },
    ]

    # 4 cards per row
    for row in range(0, len(features), 4):
        cols = st.columns(4, gap="small")
        for ci, feat in enumerate(features[row:row+4]):
            with cols[ci]:
                # Extract values into plain locals so the f-string has no dict-subscript
                # expressions and no hex-suffix ambiguity (e.g. {color}18 → invalid f-string)
                f_key   = feat["key"]
                f_icon  = feat["icon"]
                f_c1    = feat["c1"]
                f_c2    = feat["c2"]
                f_title = feat["title"]
                f_desc  = feat["desc"]
                f_btn   = feat["btn"]
                glow    = f_c1 + "18"   # e.g. "#4F46E518" – built outside the f-string
                svg_icon = _icon_card(row + ci, f_icon, f_c1, f_c2)
                st.markdown(
                    f'<div style="'
                    f'background:linear-gradient(145deg,#1E293B,#0F172A);'
                    f'border:1px solid #334155;border-radius:16px;'
                    f'padding:1.3rem;margin-bottom:0.6rem;min-height:210px;'
                    f'position:relative;overflow:hidden;">'
                    f'<div style="position:absolute;top:0;right:0;width:80px;height:80px;'
                    f'background:radial-gradient(circle,{glow} 0%,transparent 70%);'
                    f'border-radius:0 16px 0 0;"></div>'
                    f'{svg_icon}'
                    f'<div style="color:#E2E8F0;font-weight:700;font-size:0.95rem;'
                    f'margin:0.65rem 0 0.3rem 0;">{f_title}</div>'
                    f'<div style="color:#94A3B8;font-size:0.78rem;line-height:1.55;'
                    f'margin:0 0 0.8rem 0;">{f_desc}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if st.button(f_btn, key=f"feat_{f_key}", use_container_width=True):
                    st.session_state["current_page"] = f_key
                    st.rerun()

    # ── IBM Granite Banner ────────────────────────────────────────────────────
    st.markdown("""
<div style="
    background: linear-gradient(135deg, rgba(79,70,229,0.15) 0%, rgba(6,182,212,0.1) 100%);
    border: 1px solid rgba(79,70,229,0.3);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin: 1.5rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    flex-wrap: wrap;
">
    <div style="font-size:2.5rem;">🧠</div>
    <div style="flex:1;min-width:200px;">
        <div style="color:#E2E8F0;font-size:1.05rem;font-weight:700;margin-bottom:0.25rem;">
            Powered by IBM Granite via watsonx.ai
        </div>
        <div style="color:#94A3B8;font-size:0.84rem;line-height:1.6;">
            CareerMitra AI Assistant uses IBM's enterprise-grade Granite language model for
            accurate, personalised, and contextually-aware career guidance. Your data stays private.
        </div>
    </div>
    <div style="display:flex;gap:0.75rem;flex-wrap:wrap;">
        <div style="background:rgba(79,70,229,0.2);border:1px solid rgba(79,70,229,0.4);
                    border-radius:8px;padding:0.4rem 0.85rem;text-align:center;">
            <div style="color:#4F46E5;font-weight:700;font-size:0.95rem;">Granite 13B</div>
            <div style="color:#94A3B8;font-size:0.7rem;">LLM Model</div>
        </div>
        <div style="background:rgba(6,182,212,0.15);border:1px solid rgba(6,182,212,0.35);
                    border-radius:8px;padding:0.4rem 0.85rem;text-align:center;">
            <div style="color:#06B6D4;font-weight:700;font-size:0.95rem;">au-syd</div>
            <div style="color:#94A3B8;font-size:0.7rem;">Sydney Region</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── Getting Started ───────────────────────────────────────────────────────
    with st.expander("🚀 How to Get Started (5 Easy Steps)"):
        steps = [
            ("1", "#4F46E5", "👤 Build Your Profile", "Go to **Student Profile** → Fill in name, education, skills, interests → Save."),
            ("2", "#7C3AED", "🤖 Chat with AI Counselor", "Visit **AI Career Counselor** → Ask anything about your career path using IBM Granite."),
            ("3", "#06B6D4", "🎯 Get Recommendations", "Open **Career Recommendations** → See AI-matched career paths with compatibility scores."),
            ("4", "#10B981", "📊 Analyse Skill Gaps", "Use **Skill Gap Analysis** → Find out exactly which skills to learn next."),
            ("5", "#F59E0B", "🗺️ Build Your Roadmap", "Generate a **Career Roadmap** → Follow your personalised milestone plan."),
        ]
        cols = st.columns(5, gap="small")
        for col, (num, color, title, desc) in zip(cols, steps):
            with col:
                st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-top:3px solid {color};
            border-radius:10px;padding:0.9rem;text-align:center;">
    <div style="background:{color};color:white;width:28px;height:28px;border-radius:50%;
                display:flex;align-items:center;justify-content:center;
                font-weight:800;font-size:0.85rem;margin:0 auto 0.5rem auto;">{num}</div>
    <div style="color:#E2E8F0;font-weight:700;font-size:0.82rem;margin-bottom:0.3rem;">{title}</div>
    <div style="color:#94A3B8;font-size:0.73rem;line-height:1.5;">{desc}</div>
</div>
""", unsafe_allow_html=True)

    with st.expander("⚙️ IBM watsonx.ai Setup Guide"):
        st.markdown("""
**Step 1** — Create a free IBM Cloud account at [ibm.com/cloud](https://www.ibm.com/cloud)

**Step 2** — Go to [watsonx.ai](https://dataplatform.cloud.ibm.com) and create a project in the **Sydney (au-syd)** region

**Step 3** — Copy your **Project ID** from Project → Settings

**Step 4** — Generate an **API Key** from IBM Cloud → Manage → Access (IAM) → API Keys

**Step 5** — Copy `.env.example` → rename to `.env`, then fill in:
```
IBM_WATSONX_API_KEY=your_key_here
IBM_WATSONX_PROJECT_ID=your_project_id_here
IBM_WATSONX_URL=https://au-syd.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-13b-instruct-v2
```

**Step 6** — Restart the app: `python -m streamlit run app.py`

Once connected, the AI Counselor, Skill Gap Analysis, Resume Analyzer, Interview Prep, and Career Roadmap pages will use IBM Granite 13B Instruct for fully personalised AI responses.
""")
