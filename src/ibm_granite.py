# src/ibm_granite.py
# CareerMitra AI Assistant – IBM LLM Integration via IBM watsonx.ai

from __future__ import annotations
import warnings
import streamlit as st
from src.config import (
    IBM_WATSONX_API_KEY, IBM_WATSONX_PROJECT_ID, IBM_WATSONX_URL,
    GRANITE_MODEL_ID, GRANITE_PARAMS, ibm_configured,
)

# Suppress harmless SDK deprecation / third-party licence warnings that appear
# on every generate_text call and add no actionable information.
warnings.filterwarnings("ignore", category=UserWarning, module="ibm_watsonx_ai")
try:
    from ibm_watsonx_ai.wml_resource import WatsonxAPIWarning  # type: ignore
    warnings.filterwarnings("ignore", category=WatsonxAPIWarning)
except ImportError:
    pass

# ── Lazy import guard: ibm-watsonx-ai may not be installed in all envs ────────
_client_cache: dict = {}


def _get_model():
    """Return a cached ModelInference instance, or None if not configured."""
    if "model" in _client_cache:
        return _client_cache["model"]

    if not ibm_configured():
        return None

    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference

        creds = Credentials(url=IBM_WATSONX_URL, api_key=IBM_WATSONX_API_KEY)
        model = ModelInference(
            model_id=GRANITE_MODEL_ID,
            credentials=creds,
            project_id=IBM_WATSONX_PROJECT_ID,
            params=GRANITE_PARAMS,
        )
        _client_cache["model"] = model
        return model
    except ImportError:
        _client_cache["model"] = None
        _client_cache["error"] = "ibm-watsonx-ai package not installed. Run: pip install ibm-watsonx-ai"
        return None
    except Exception as e:
        _client_cache["model"] = None
        err_str = str(e)
        # Provide a user-friendly message for the most common configuration errors
        if "WSCPA404PE" in err_str or "not_found: missing" in err_str:
            _client_cache["error"] = (
                f"⚠️ **IBM watsonx.ai Project Not Found**\n\n"
                f"Project ID `{IBM_WATSONX_PROJECT_ID}` does not exist on region `{IBM_WATSONX_URL}`.\n\n"
                f"**Fix:** Go to [watsonx.ai](https://dataplatform.cloud.ibm.com) → Your project → Settings "
                f"and verify the region. Ensure the project exists in the **Sydney (au-syd)** region, "
                f"copy the Project ID, and update `IBM_WATSONX_PROJECT_ID` in your `.env` file."
            )
        elif "no_associated_service_instance" in err_str:
            _client_cache["error"] = (
                f"⚠️ **IBM Machine Learning instance not associated**\n\n"
                f"The project `{IBM_WATSONX_PROJECT_ID}` exists but has no Watson Machine Learning "
                f"service instance linked to it.\n\n"
                f"**Fix:** Go to your watsonx.ai project → Manage → Services & integrations → "
                f"Associate a Watson Machine Learning instance."
            )
        elif "403" in err_str or "Unauthorized" in err_str or "authentication" in err_str.lower():
            _client_cache["error"] = (
                f"⚠️ **IBM API Key authentication failed**\n\n"
                f"The API key in your `.env` is invalid or expired.\n\n"
                f"**Fix:** Go to IBM Cloud → Manage → Access (IAM) → API Keys and regenerate your key."
            )
        elif "not supported" in err_str.lower() or "Supported models" in err_str:
            # Extract the supported models list from the error message if present
            import re
            supported_match = re.search(r"Supported models:\s*(\[.+?\])", err_str, re.DOTALL)
            supported_hint  = supported_match.group(1) if supported_match else "check your watsonx.ai project"
            _client_cache["error"] = (
                f"⚠️ **Model not available in this project**\n\n"
                f"Model `{GRANITE_MODEL_ID}` is not enabled for project `{IBM_WATSONX_PROJECT_ID}`.\n\n"
                f"**Available models:** {supported_hint}\n\n"
                f"**Fix:** Update `GRANITE_MODEL_ID` in your `.env` to one of the supported models above, "
                f"or go to your watsonx.ai project → Assets → Foundation models and add the model."
            )
        else:
            _client_cache["error"] = f"IBM connection error: {err_str}"
        return None


def get_model_error() -> str | None:
    """Return the last model initialisation error message, if any."""
    return _client_cache.get("error")


# ── Prompt templates ──────────────────────────────────────────────────────────

def _career_counselor_prompt(student_context: str, conversation: list[dict], user_message: str) -> str:
    """Build an instruction-style prompt for Granite."""
    history_text = ""
    for turn in conversation[-6:]:   # last 3 pairs
        role_label = "Student" if turn["role"] == "user" else "CareerMitra"
        history_text += f"{role_label}: {turn['content']}\n"

    return f"""You are CareerMitra, a highly experienced AI career counselor specialising in Indian and global career guidance for students.

Your responsibilities:
- Provide personalised, actionable career advice
- Recommend career paths based on the student's education, skills, and interests
- Suggest certifications, courses, and skill development strategies
- Share Indian job market insights (IITs, IIMs, UPSC, CAT, GATE, etc.)
- Be encouraging, professional, and student-centric

Student Profile:
{student_context}

Conversation so far:
{history_text}
Student: {user_message}
CareerMitra:"""


def _skill_gap_prompt(domain: str, current_skills: list[str], required_skills: list[str]) -> str:
    missing = [s for s in required_skills if s not in current_skills]
    return f"""You are a career skill advisor. Analyse the skill gap for a student targeting {domain}.

Current skills: {', '.join(current_skills) if current_skills else 'None listed'}
Required skills for {domain}: {', '.join(required_skills)}
Missing skills: {', '.join(missing) if missing else 'None — student meets requirements'}

Provide a concise, actionable skill gap analysis in 3–5 bullet points. Include specific learning resources.
Analysis:"""


def _roadmap_prompt(domain: str, role: str, timeline: str, current_skills: list[str]) -> str:
    return f"""You are a career roadmap expert. Create a personalised career roadmap.

Target Career: {role} in {domain}
Timeline: {timeline}
Current Skills: {', '.join(current_skills) if current_skills else 'Basic level'}

Generate a step-by-step career roadmap with 4 phases. Each phase should have 3–4 specific, actionable milestones.
Format as: Phase Name → Milestone 1, Milestone 2, Milestone 3
Roadmap:"""


def _recommendation_prompt(education: str, stream: str, skills: list[str], interests: list[str]) -> str:
    return f"""You are a career recommendation expert for Indian students.

Student Background:
- Education: {education}
- Stream/Branch: {stream}
- Skills: {', '.join(skills[:10]) if skills else 'Not specified'}
- Interests: {', '.join(interests[:8]) if interests else 'Not specified'}

Recommend the top 3 most suitable career paths. For each, provide:
1. Career Domain
2. Best-fit job roles (2–3 roles)
3. Why it matches this student (1–2 sentences)
4. Key skills to develop

Career Recommendations:"""


# ── Public API ────────────────────────────────────────────────────────────────

def granite_chat(student_context: str, conversation: list[dict], user_message: str) -> str:
    """
    Send a chat turn to IBM Granite and return the response string.
    Falls back to a demo response if credentials are not configured.
    """
    model = _get_model()

    if model is None:
        return _demo_counselor_response(user_message)

    prompt = _career_counselor_prompt(student_context, conversation, user_message)
    try:
        result = model.generate_text(prompt=prompt)
        return result.strip() if result else "I couldn't generate a response. Please try again."
    except Exception as e:
        return f"⚠️ IBM Granite error: {str(e)}\n\n{_demo_counselor_response(user_message)}"


def granite_skill_gap_analysis(domain: str, current_skills: list[str], required_skills: list[str]) -> str:
    """Generate an AI skill gap analysis using IBM Granite."""
    model = _get_model()
    if model is None:
        return _demo_skill_gap(domain, current_skills, required_skills)

    prompt = _skill_gap_prompt(domain, current_skills, required_skills)
    try:
        result = model.generate_text(prompt=prompt)
        return result.strip() if result else ""
    except Exception as e:
        return f"⚠️ IBM Granite error: {str(e)}"


def granite_roadmap(domain: str, role: str, timeline: str, current_skills: list[str]) -> str:
    """Generate a personalised career roadmap using IBM Granite."""
    model = _get_model()
    if model is None:
        return _demo_roadmap(domain, role)

    prompt = _roadmap_prompt(domain, role, timeline, current_skills)
    try:
        result = model.generate_text(prompt=prompt)
        return result.strip() if result else ""
    except Exception as e:
        return f"⚠️ IBM Granite error: {str(e)}"


def granite_career_recommendations(education: str, stream: str, skills: list[str], interests: list[str]) -> str:
    """Generate career recommendations using IBM Granite."""
    model = _get_model()
    if model is None:
        return _demo_recommendations(stream)

    prompt = _recommendation_prompt(education, stream, skills, interests)
    try:
        result = model.generate_text(prompt=prompt)
        return result.strip() if result else ""
    except Exception as e:
        return f"⚠️ IBM Granite error: {str(e)}"


# ── Demo / fallback responses (shown when IBM credentials not set) ─────────────

def _demo_counselor_response(user_message: str) -> str:
    lower = user_message.lower()
    if any(k in lower for k in ["pcm", "science", "engineering", "b.tech", "iit"]):
        return """Based on your Science (PCM) background, here are your strongest career paths:

**🔥 Top Recommendations:**

1. **Software Engineering / Computer Science** — India's #1 hiring domain with 200K+ openings annually. Start with Python and DSA.

2. **Data Science & AI/ML** — With PCM fundamentals, you can excel in statistics-heavy ML roles. Avg salary: ₹15–30 LPA.

3. **Cloud & DevOps Engineering** — AWS/Azure certifications open doors at TCS, Infosys, Amazon, and startups.

**Immediate Next Steps:**
- Prepare for **JEE** (for IITs/NITs) or **BITSAT/VIT** for top private colleges
- Start Python on freeCodeCamp — it's free and comprehensive
- Join competitive programming on LeetCode or Codeforces

Which path excites you most? I can create a detailed 2-year roadmap! 🚀

*Note: Connect IBM watsonx.ai credentials in .env for fully personalised AI responses.*"""
    if any(k in lower for k in ["mba", "management", "business", "commerce"]):
        return """For a career in Business & Management, here's your roadmap:

**🎯 Top Career Paths:**

1. **Management Consulting** — McKinsey, BCG, Deloitte. Requires strong analytical + communication skills.
2. **Product Management** — Bridge between tech and business. Avg salary: ₹20–40 LPA.
3. **Investment Banking / FinTech** — High-earning track in finance.

**Key Steps:**
- Target **CAT/GMAT** for IIM/top B-school admission
- Build Excel + Power BI + SQL skills for analytics roles
- Do 2 internships before applying to B-schools

What's your current education level? I'll tailor the advice further!

*Note: Connect IBM watsonx.ai credentials in .env for fully personalised AI responses.*"""
    return """Great question! As your CareerMitra AI counselor, here's my advice:

**Understanding your career options starts with 3 questions:**
1. What subjects do you genuinely enjoy?
2. What kind of work environment suits you — office, field, creative, technical?
3. What's your target income in 5 years?

**Popular high-growth careers in India (2025):**
- 🤖 **AI/ML Engineer** — ₹18–45 LPA | Very High Demand
- ☁️ **Cloud Architect** — ₹15–35 LPA | High Demand
- 💰 **FinTech Analyst** — ₹12–28 LPA | Growing Fast
- 🏥 **Healthcare Technology** — ₹10–25 LPA | Stable Growth

Tell me more about your background and I'll give you a personalised recommendation!

*Note: Add IBM watsonx.ai credentials to your .env file for full AI-powered personalisation.*"""


def _demo_skill_gap(domain: str, current: list[str], required: list[str]) -> str:
    missing = [s for s in required if s not in current]
    lines = [f"**Skill Gap Analysis for {domain}** *(Demo Mode)*\n"]
    if missing:
        lines.append(f"**Missing Skills ({len(missing)}):** {', '.join(missing)}\n")
        lines.append("**Recommended Actions:**")
        for s in missing[:4]:
            lines.append(f"• Learn **{s}**: Search Coursera, edX, or YouTube for '{s} course for beginners'")
    else:
        lines.append("✅ You meet all skill requirements for this career domain!")
    lines.append("\n*Connect IBM watsonx.ai for deeper AI-powered analysis.*")
    return "\n".join(lines)


def _demo_roadmap(domain: str, role: str) -> str:
    return f"""**Career Roadmap: {role} in {domain}** *(Demo Mode)*

**Phase 1 — Foundation (0–6 months)**
→ Take a foundational course in your core subject area
→ Build basic projects and a GitHub portfolio
→ Join professional communities (LinkedIn, Discord)

**Phase 2 — Skill Building (6–18 months)**
→ Complete 2 industry-recognised certifications
→ Contribute to open-source or internship projects
→ Network with 20+ professionals in your target field

**Phase 3 — Specialisation (18–30 months)**
→ Choose a high-demand sub-domain and go deep
→ Build a capstone project solving a real problem
→ Apply for internships or junior roles

**Phase 4 — Career Launch (30+ months)**
→ Land your first role at a target company
→ Continuously learn and grow within the organisation
→ Begin mentoring others in 2–3 years

*Connect IBM watsonx.ai credentials for a fully personalised AI-generated roadmap.*"""


def _demo_recommendations(stream: str) -> str:
    recs = {
        "Science (PCM)": "Technology & Engineering, Data Science & AI/ML, Finance & Accounting",
        "Science (PCB)": "Healthcare & Medicine, Biotech Research, Clinical Data Science",
        "Commerce": "Finance & Accounting, Business & Management, Sales & Marketing",
        "Arts / Humanities": "Education & Research, Creative Arts & Design, Law & Policy",
        "Engineering": "Technology & Engineering, Data Science & AI/ML, Operations & Logistics",
        "Computer Science": "Data Science & AI/ML, Technology & Engineering, Sales & Marketing",
    }
    match = recs.get(stream, "Technology & Engineering, Business & Management, Creative Arts & Design")
    return f"**Top Career Matches for {stream}:** {match}\n\n*Connect IBM watsonx.ai for detailed AI recommendations.*"
