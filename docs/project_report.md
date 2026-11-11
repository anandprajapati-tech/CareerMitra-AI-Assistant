# CareerMitra AI – Project Report

**Project Title:** CareerMitra AI – Agentic Career Counseling Companion  
**Technology Stack:** Python · Streamlit · IBM Granite (watsonx.ai) · SQLite · Plotly · Pandas  
**Version:** 2.0.0  
**Date:** November 2026  
**Region:** IBM Cloud Sydney (au-syd)

---

## 1. Executive Summary

CareerMitra AI is an intelligent, multi-agent career counseling application designed to bridge the career guidance gap for students in India. Leveraging IBM Granite — a foundation large language model (LLM) accessed via IBM watsonx.ai — the system provides personalised career recommendations, skill gap analysis, career roadmaps, and conversational AI counseling.

The application addresses a critical real-world problem: millions of Indian students make career decisions without access to qualified counselors, often relying on peer pressure or incomplete information. CareerMitra AI acts as a 24/7 accessible, AI-powered career mentor.

---

## 2. Problem Statement

### 2.1 Background

India produces over 3 million engineering graduates and 1.5 million business graduates annually. A significant proportion (estimated 45–60%) end up in roles misaligned with their skills, interests, or potential — leading to low productivity, job dissatisfaction, and high attrition rates.

### 2.2 Key Pain Points

| Pain Point | Impact |
|---|---|
| Lack of access to professional career counselors | Most tier-2/3 city students have no access |
| Information asymmetry about job market realities | Students choose careers based on hearsay |
| No skill-gap visibility | Students don't know what skills they need |
| No personalised roadmaps | Generic advice doesn't account for individual backgrounds |
| Language barrier | English-only tools exclude Hindi/Hinglish speakers |

---

## 3. Solution: CareerMitra AI

### 3.1 Core Features

| Feature | Description |
|---|---|
| **Student Profile** | Multi-tab form capturing education, skills (with proficiency levels), interests, and career goals |
| **IBM Granite AI Counselor** | Persistent chat with IBM Granite LLM; maintains conversation history in SQLite |
| **Career Recommendations** | Scoring engine (skills + interests + stream alignment) across 10 career domains |
| **Skill Gap Analysis** | Radar chart + per-skill progress bars showing current vs required proficiency |
| **Career Roadmap** | Phase-by-phase milestone templates + IBM Granite-generated personalised plans |
| **Job Market Insights** | Salary benchmarks, demand trends, top hiring companies, future outlook |
| **Progress Dashboard** | Milestone tracker with checkboxes, skill portfolio charts, KPI summary |
| **Multilingual Support** | AI counselor supports Hindi, English, and Hinglish prompts |

### 3.2 Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Streamlit UI (app.py)              │
├─────────────┬───────────────────────────────────────┤
│  src/pages/ │  8 page modules (render_* functions)  │
├─────────────┴───────────────────────────────────────┤
│              src/ (Business Logic Layer)             │
│  config.py  │  ibm_granite.py  │  database.py       │
│  career_recommendation.py  │  skill_gap_analysis.py │
│  career_roadmap.py         │  progress_tracking.py  │
├─────────────────────────────────────────────────────┤
│         IBM watsonx.ai (au-syd region)               │
│         IBM Granite 13B Instruct / 3-8B Instruct    │
├─────────────────────────────────────────────────────┤
│         SQLite Database (data/careermitra.db)        │
│  students │ student_skills │ student_interests      │
│  career_goals │ counselor_sessions │ recommendations│
│  progress_milestones                                │
└─────────────────────────────────────────────────────┘
```

---

## 4. Technical Implementation

### 4.1 IBM Granite Integration

The IBM Granite LLM is integrated via the `ibm-watsonx-ai` Python SDK:

```python
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

creds = Credentials(url="https://au-syd.ml.cloud.ibm.com", api_key=API_KEY)
model = ModelInference(model_id="ibm/granite-13b-instruct-v2",
                       credentials=creds, project_id=PROJECT_ID,
                       params={"max_new_tokens": 800, "temperature": 0.7})
response = model.generate_text(prompt=prompt)
```

**Prompt Engineering Strategy:**
- Instruction-style prompts with student context injected at the top
- Last 3 conversation turns included for conversational continuity
- Domain-specific prompts for skill gap, roadmap, and recommendations
- Graceful fallback to curated demo responses when IBM credentials are not configured

### 4.2 Credential Security

| Practice | Implementation |
|---|---|
| Credentials in `.env` file | Loaded via `python-dotenv` |
| `.env` excluded from git | Listed in `.gitignore` |
| API key never printed | Not logged, not shown in UI |
| `.env.example` provided | Contains only placeholder structure |
| Demo mode | App works without credentials |

### 4.3 Database Schema

All student data is persisted in SQLite (`data/careermitra.db`):

```sql
students            -- core student profile
student_skills      -- skills with proficiency levels
student_interests   -- areas of interest
career_goals        -- target domain, role, and timeline
counselor_sessions  -- full IBM Granite chat history
recommendations     -- scored career domain recommendations
progress_milestones -- learning milestones with completion flags
```

### 4.4 Career Recommendation Engine

The scoring algorithm (`src/career_recommendation.py`) computes a 0–100 match score:

| Component | Max Points | Logic |
|---|---|---|
| Skill match | 45 pts | 15 pts per matching required skill |
| Interest match | 35 pts | 20 pts per matching domain interest |
| Stream alignment | 20 pts | Full points if academic stream matches domain |

### 4.5 Skill Gap Analysis

The `src/skill_gap_analysis.py` module compares student proficiency against per-domain benchmarks:

| Proficiency | Score |
|---|---|
| Beginner | 25 |
| Intermediate | 50 |
| Advanced | 75 |
| Expert | 100 |

---

## 5. Project File Structure

```
CAREERMITRA AI/
├── app.py                        # Main Streamlit entry point
├── requirements.txt              # Python dependencies
├── README.md                     # Setup and usage documentation
├── .env                          # Local credentials (not committed)
├── .env.example                  # Credential template (safe to commit)
├── .gitignore                    # Excludes .env, __pycache__, *.db
│
├── src/
│   ├── __init__.py
│   ├── config.py                 # App config, IBM credentials, constants
│   ├── database.py               # SQLite CRUD operations
│   ├── ibm_granite.py            # IBM Granite LLM integration + fallback
│   ├── career_recommendation.py  # Career domain scoring engine
│   ├── skill_gap_analysis.py     # Skill gap computation helpers
│   ├── career_roadmap.py         # Roadmap templates and logic
│   ├── progress_tracking.py      # Milestone and progress helpers
│   └── pages/
│       ├── home.py               # Landing page
│       ├── student_profile.py    # Profile management
│       ├── ai_counselor.py       # IBM Granite chat interface
│       ├── career_recommendations.py  # Recommendations with charts
│       ├── skill_gap.py          # Radar chart + gap breakdown
│       ├── roadmap.py            # Roadmap renderer + goal setting
│       ├── job_market.py         # Salary and demand insights
│       └── dashboard.py          # Progress dashboard
│
├── data/
│   ├── career_data.json          # Career domains reference data
│   └── careermitra.db            # SQLite database (auto-created)
│
└── docs/
    ├── project_report.md         # This document
    └── CareerMitra_AI_Presentation.pptx
```

---

## 6. IBM watsonx.ai Configuration

### 6.1 Region

CareerMitra AI is configured to use the **Sydney (au-syd)** region:

```
IBM_WATSONX_URL=https://au-syd.ml.cloud.ibm.com
```

### 6.2 Model

```
GRANITE_MODEL_ID=ibm/granite-13b-instruct-v2
```

Alternative: `ibm/granite-3-8b-instruct` (lighter, faster)

### 6.3 Important: Project ID Must Match Region

IBM watsonx.ai projects are **region-specific**. If the Project ID was created in a different region (e.g., `us-south`), it will not be found on `au-syd`.

**To fix:** Create a new project in [watsonx.ai Sydney](https://dataplatform.cloud.ibm.com), copy the new Project ID, and update `IBM_WATSONX_PROJECT_ID` in `.env`.

---

## 7. Demo Mode

When IBM credentials are not configured or the project cannot be reached, CareerMitra AI automatically switches to **Demo Mode**:

- All pages and features remain fully functional
- AI modules return curated, educationally accurate demo responses
- The sidebar shows a yellow "Demo Mode" badge
- The AI Counselor page shows a clear error message explaining how to fix the configuration

---

## 8. Languages Supported

| Language | Support |
|---|---|
| English | Full — all UI, prompts, and responses |
| Hindi | AI counselor accepts Hindi prompts and responds in Hindi if prompted |
| Hinglish | AI counselor naturally handles mixed Hindi-English input |

---

## 9. Testing Summary

| Test Area | Result |
|---|---|
| Python package installation | ✅ All packages installed |
| `.env` credential loading | ✅ Loaded correctly via python-dotenv |
| IBM watsonx.ai API key validity | ✅ API key authenticates to au-syd |
| IBM Granite model access | ⚠️ Project ID not found in au-syd (see §6.3) |
| SQLite database init | ✅ Tables created on first run |
| App startup (streamlit run app.py) | ✅ App starts in Demo Mode |
| Student profile creation | ✅ Form saves to SQLite |
| Career recommendation scoring | ✅ Scores computed correctly |
| Skill gap analysis | ✅ Gap computed and radar chart renders |
| Career roadmap | ✅ Templates render; AI roadmap works in Demo Mode |
| Progress dashboard | ✅ Milestones, KPIs, and charts render |
| Navigation | ✅ All 8 pages accessible via sidebar |

---

## 10. How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure credentials
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
# Edit .env — add your IBM_WATSONX_API_KEY and IBM_WATSONX_PROJECT_ID

# 3. Run the application
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 11. Limitations

| Limitation | Notes |
|---|---|
| Job vacancy data | Not real-time; uses static reference data for India 2025 |
| Salary figures | Approximate ranges; not live market data |
| IBM Granite Project ID | Must be created in the au-syd region |
| Multilingual UI | UI labels are in English; AI content can be in Hindi |

---

## 12. Future Enhancements

- Resume parser: Extract skills from uploaded PDF resume
- Real-time job listings via LinkedIn/Naukri API
- PDF report export for career counseling report
- Peer comparison: Anonymised benchmarking against other students
- Gamification: Badges and streaks for milestone completion
- WhatsApp / Telegram bot integration for wider student reach

---

*Built with ❤️ using IBM Granite and Streamlit — CareerMitra AI is designed for Indian students navigating their career journey.*
