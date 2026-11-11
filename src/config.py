# src/config.py
# CareerMitra AI Assistant – Centralised configuration (IBM watsonx.ai edition)

import os
from dotenv import load_dotenv

load_dotenv()

# ── App Identity ──────────────────────────────────────────────────────────────
APP_NAME        = os.getenv("APP_NAME", "CareerMitra AI Assistant")
APP_SUBTITLE    = "Your Intelligent AI Career Companion"
APP_TAGLINE     = "Discover Your Potential, Build Your Future."
APP_VERSION     = "2.0.0"
APP_ICON        = "🎓"
DEBUG           = os.getenv("APP_DEBUG", "False").lower() == "true"

# ── IBM watsonx.ai ────────────────────────────────────────────────────────────
IBM_WATSONX_API_KEY    = os.getenv("IBM_WATSONX_API_KEY", "")
IBM_WATSONX_PROJECT_ID = os.getenv("IBM_WATSONX_PROJECT_ID", "")
IBM_WATSONX_URL        = os.getenv("IBM_WATSONX_URL", "https://au-syd.ml.cloud.ibm.com")
GRANITE_MODEL_ID       = os.getenv("GRANITE_MODEL_ID", "ibm/granite-13b-instruct-v2")

# Granite generation parameters
GRANITE_PARAMS = {
    "max_new_tokens": 800,
    "min_new_tokens": 20,
    "temperature": 0.7,
    "top_p": 0.9,
    "repetition_penalty": 1.1,
}

# ── Database ──────────────────────────────────────────────────────────────────
DB_PATH = os.path.join("data", "careermitra.db")

# ── Career Domains ────────────────────────────────────────────────────────────
CAREER_DOMAINS = [
    "Technology & Engineering",
    "Data Science & AI/ML",
    "Business & Management",
    "Healthcare & Medicine",
    "Creative Arts & Design",
    "Education & Research",
    "Finance & Accounting",
    "Sales & Marketing",
    "Operations & Logistics",
    "Law & Policy",
]

# ── Education Levels ──────────────────────────────────────────────────────────
EDUCATION_LEVELS = [
    "High School (10th)",
    "Higher Secondary (12th)",
    "Diploma",
    "Bachelor's Degree",
    "Master's Degree",
    "PhD / Doctoral",
    "Professional Certification",
]

# ── Academic Streams ──────────────────────────────────────────────────────────
STREAMS = [
    "Science (PCM)",
    "Science (PCB)",
    "Commerce",
    "Arts / Humanities",
    "Engineering",
    "Medical",
    "Computer Science",
    "Other",
]

# ── Skill Categories ──────────────────────────────────────────────────────────
SKILL_CATEGORIES = {
    "Technical": [
        "Python", "Java", "C++", "JavaScript", "SQL", "Machine Learning",
        "Data Analysis", "Cloud Computing", "DevOps", "Cybersecurity",
        "Web Development", "Mobile Development", "Blockchain", "R Programming",
    ],
    "Analytical": [
        "Problem Solving", "Critical Thinking", "Research", "Data Visualization",
        "Statistical Analysis", "Business Analysis", "Financial Modeling",
    ],
    "Communication": [
        "Public Speaking", "Technical Writing", "Presentation Skills",
        "Negotiation", "Storytelling", "Report Writing",
    ],
    "Soft Skills": [
        "Leadership", "Teamwork", "Time Management", "Adaptability",
        "Emotional Intelligence", "Project Management", "Networking",
    ],
}

PROFICIENCY_LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"]

# ── Interests ─────────────────────────────────────────────────────────────────
INTERESTS = [
    "Programming & Coding", "Mathematics & Statistics", "Biology & Life Sciences",
    "Business & Entrepreneurship", "Art & Design", "Music & Performing Arts",
    "Writing & Literature", "Social Work & NGOs", "Finance & Investment",
    "Healthcare & Wellness", "Teaching & Mentoring", "Sports & Fitness",
    "Environment & Sustainability", "Government & Politics", "Travel & Tourism",
]

# ── UI Navigation Pages ───────────────────────────────────────────────────────
PAGES = [
    {"name": "🏠 Home Dashboard",           "key": "home",            "icon": "🏠"},
    {"name": "👤 Student Profile",           "key": "profile",         "icon": "👤"},
    {"name": "🤖 AI Career Counselor",       "key": "counselor",       "icon": "🤖"},
    {"name": "🎯 Career Recommendations",    "key": "recommendations", "icon": "🎯"},
    {"name": "📊 Skill Gap Analysis",        "key": "skill_gap",       "icon": "📊"},
    {"name": "🗺️ Career Roadmap",            "key": "roadmap",         "icon": "🗺️"},
    {"name": "📈 Job Market Insights",       "key": "job_market",      "icon": "📈"},
    {"name": "📄 Resume Analyzer",           "key": "resume",          "icon": "📄"},
    {"name": "🎤 AI Interview Prep",         "key": "interview",       "icon": "🎤"},
    {"name": "📋 Progress Dashboard",        "key": "dashboard",       "icon": "📋"},
    {"name": "⚙️ Settings",                  "key": "settings",        "icon": "⚙️"},
]

# ── UI Theme Colors ───────────────────────────────────────────────────────────
COLORS = {
    "primary":    "#4F46E5",
    "secondary":  "#7C3AED",
    "accent":     "#06B6D4",
    "success":    "#10B981",
    "warning":    "#F59E0B",
    "danger":     "#EF4444",
    "bg_dark":    "#0F172A",
    "bg_card":    "#1E293B",
    "text_light": "#F1F5F9",
    "text_muted": "#94A3B8",
    "border":     "#334155",
}

def ibm_configured() -> bool:
    """Return True if IBM watsonx.ai credentials are present."""
    return bool(IBM_WATSONX_API_KEY and IBM_WATSONX_PROJECT_ID
                and IBM_WATSONX_API_KEY != "your_ibm_watsonx_api_key_here")
