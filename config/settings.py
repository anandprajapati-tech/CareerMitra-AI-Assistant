# config/settings.py
# CareerMitra AI – Application Configuration and Constants

import os
from dotenv import load_dotenv

load_dotenv()

# ── App Identity ──────────────────────────────────────────────────────────────
APP_NAME = "CareerMitra AI"
APP_SUBTITLE = "Agentic Career Counseling Companion"
APP_VERSION = "1.0.0"
APP_ICON = "🎓"

# ── OpenAI / LLM ──────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = "gpt-4o-mini"          # cost-effective default; change to gpt-4 for production
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 1500

# ── Database ──────────────────────────────────────────────────────────────────
DB_PATH = "data/careermitra.db"

# ── Career Domains ────────────────────────────────────────────────────────────
CAREER_DOMAINS = [
    "Technology & Engineering",
    "Data Science & AI/ML",
    "Business & Management",
    "Healthcare & Medicine",
    "Creative Arts & Design",
    "Education & Research",
    "Finance & Accounting",
    "Law & Policy",
    "Sales & Marketing",
    "Operations & Logistics",
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

# ── Streams ───────────────────────────────────────────────────────────────────
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
        "Web Development", "Mobile Development", "Blockchain",
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

# ── Proficiency Levels ────────────────────────────────────────────────────────
PROFICIENCY_LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"]

# ── Interests ─────────────────────────────────────────────────────────────────
INTERESTS = [
    "Programming & Coding", "Mathematics & Statistics", "Biology & Life Sciences",
    "Business & Entrepreneurship", "Art & Design", "Music & Performing Arts",
    "Writing & Literature", "Social Work & NGOs", "Finance & Investment",
    "Healthcare & Wellness", "Teaching & Mentoring", "Sports & Fitness",
    "Environment & Sustainability", "Government & Politics", "Travel & Tourism",
]

# ── Navigation Pages ──────────────────────────────────────────────────────────
PAGES = [
    {"name": "🏠 Home", "key": "home"},
    {"name": "👤 Student Profile", "key": "profile"},
    {"name": "🤖 AI Counselor", "key": "counselor"},
    {"name": "🎯 Career Recommendations", "key": "recommendations"},
    {"name": "📊 Skill Gap Analysis", "key": "skill_gap"},
    {"name": "🗺️ Career Roadmap", "key": "roadmap"},
    {"name": "📈 Job Market Insights", "key": "job_market"},
    {"name": "📋 Progress Dashboard", "key": "dashboard"},
]

# ── UI Theme Colors ───────────────────────────────────────────────────────────
COLORS = {
    "primary": "#4F46E5",       # Indigo
    "secondary": "#7C3AED",     # Violet
    "accent": "#06B6D4",        # Cyan
    "success": "#10B981",       # Emerald
    "warning": "#F59E0B",       # Amber
    "danger": "#EF4444",        # Red
    "bg_dark": "#0F172A",       # Slate 900
    "bg_card": "#1E293B",       # Slate 800
    "text_light": "#F1F5F9",    # Slate 100
    "text_muted": "#94A3B8",    # Slate 400
}
