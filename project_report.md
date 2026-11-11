# CareerMitra AI – Project Report

**Project Title:** CareerMitra AI – Agentic Career Counseling Companion  
**Technology Stack:** Python · Streamlit · IBM Granite (watsonx.ai) · SQLite · Plotly · Pandas  
**Version:** 2.0.0  
**Date:** November 2026

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
| Generic advice that doesn't account for individual strengths | One-size-fits-all counseling is ineffective |
| No structured roadmap | Students lack step-by-step career plans |

### 2.3 Opportunity

An AI-powered, always-available career counselor that:
- Uses the student's actual profile (education, skills, interests)
- Provides real Indian job market data
- Identifies skill gaps with precision
- Generates personalised roadmaps
- Supports ongoing conversation through an LLM

---

## 3. Solution Architecture

### 3.1 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CareerMitra AI v2.0                       │
│                  (Streamlit Web Application)                 │
├────────────────┬────────────────────┬───────────────────────┤
│  Student UI    │   Agent Modules    │    Data Layer         │
│                │                    │                       │
│  Home          │  Profile Agent     │  SQLite Database      │
│  Profile Form  │  Counselor Agent   │  career_data.json     │
│  Chat UI       │  Recommender       │                       │
│  Skill Gap     │  Gap Analyser      │                       │
│  Roadmap       │  Roadmap Generator │                       │
│  Job Market    │  Insights Agent    │                       │
│  Dashboard     │                    │                       │
└────────────────┴──────────┬─────────┴───────────────────────┘
                            │
                    ┌───────▼──────────┐
                    │  IBM watsonx.ai   │
                    │  IBM Granite LLM  │
                    │  (granite-13b-    │
                    │   instruct-v2)    │
                    └──────────────────┘
```

### 3.2 Multi-Agent Design

The application implements a lightweight multi-agent pattern where each module acts as a specialised agent:

| Agent | Responsibility | IBM Granite Role |
|---|---|---|
| **Profile Agent** | Collects & validates student data | None (form-based) |
| **Counselor Agent** | Conversational career advisor | Primary LLM interaction |
| **Recommendation Agent** | Matches student to career paths | AI narrative analysis |
| **Gap Analysis Agent** | Skill gap scoring + learning resources | AI-enhanced recommendations |
| **Roadmap Agent** | Phase-based career planning | AI-generated personalised plans |
| **Insights Agent** | Job market data visualisation | None (static data + charts) |

### 3.3 IBM Granite Integration

IBM Granite is integrated through the `ibm-watsonx-ai` Python SDK:

```python
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

creds = Credentials(url=IBM_WATSONX_URL, api_key=IBM_WATSONX_API_KEY)
model = ModelInference(
    model_id="ibm/granite-13b-instruct-v2",
    credentials=creds,
    project_id=IBM_WATSONX_PROJECT_ID,
    params={"max_new_tokens": 800, "temperature": 0.7, "top_p": 0.9}
)
response = model.generate_text(prompt=prompt)
```

**Prompt Engineering:** Custom instruction-format prompts are used for each agent. Student profile context is injected into the system prompt to personalise every response.

---

## 4. Technical Implementation

### 4.1 Technology Stack

| Component | Technology | Justification |
|---|---|---|
| Web UI | Streamlit 1.32+ | Rapid prototyping, Python-native, zero JS required |
| LLM | IBM Granite 13B | Free via watsonx.ai, instruction-tuned, enterprise-grade |
| Database | SQLite | Zero-config, embedded, perfect for single-user deployment |
| Visualisation | Plotly 5.18+ | Interactive charts, dark theme support |
| Data Processing | Pandas + NumPy | Standard Python data science stack |
| Config | python-dotenv | Industry-standard secret management |

### 4.2 Database Design

The SQLite database uses 7 tables with foreign key relationships:

```sql
students → student_skills       (1:many)
students → student_interests    (1:many)
students → career_goals         (1:many)
students → counselor_sessions   (1:many)
students → recommendations      (1:many)
students → progress_milestones  (1:many)
```

### 4.3 Skill Scoring Algorithm

The career recommendation engine uses a multi-factor weighted scoring model:

```
Score = Skill Overlap (45%) + Interest Alignment (35%) + Stream Match (20%)

Where:
- Skill Overlap = (matching skills / required skills) × 45
- Interest Alignment = (matching interests / relevant interests) × 35  
- Stream Match = 20 if student's stream matches domain's typical streams
```

### 4.4 File Structure

```
app.py                     → Entry point, routing, sidebar, CSS
src/config.py              → All constants, IBM credentials, page config
src/database.py            → All SQLite CRUD operations (270+ lines)
src/ibm_granite.py         → IBM SDK wrapper, prompts, fallback responses
src/pages/home.py          → Landing page with feature overview
src/pages/student_profile.py → Multi-tab profile form
src/pages/ai_counselor.py  → Chat UI with IBM Granite
src/pages/career_recommendations.py → Scoring + AI analysis
src/pages/skill_gap.py     → Radar chart + gap breakdown + AI
src/pages/roadmap.py       → Templates + AI roadmap generation
src/pages/job_market.py    → Charts from static 2025 data
src/pages/dashboard.py     → KPIs, milestones, skill charts
data/career_data.json      → 8 career domains with roles, salaries, skills
```

---

## 5. Key Features

### 5.1 Student Profile
- Multi-tab form: Basic Info → Skills → Interests
- 50+ skills across 4 categories with proficiency levels
- 15 interest areas
- Persistent SQLite storage per student (email as key)
- Profile completion indicator

### 5.2 AI Career Counselor (IBM Granite)
- Conversational chat interface
- Student profile injected as context into every prompt
- 20-turn conversation history maintained
- Demo responses for no-credential mode
- Clear chat and session management

### 5.3 Career Recommendations
- Multi-factor scoring across 8 career domains
- Top 3 match cards with medals and demand badges
- Horizontal bar chart for full domain comparison
- IBM Granite narrative analysis on demand
- Domain deep-dive with roles, skills, companies, salary

### 5.4 Skill Gap Analysis
- Radar chart: current vs required proficiency
- Skill-by-skill progress bars with status indicators
- IBM Granite AI analysis with actionable advice
- Auto-generate learning milestones from identified gaps
- Links to specific learning resources (Coursera, Kaggle, etc.)

### 5.5 Career Roadmap
- 4-domain templates (Tech, Data Science, Business, Finance)
- Phase-based view with expandable milestone lists
- IBM Granite personalised roadmap on demand
- Goal-saving with timeline and target role

### 5.6 Job Market Insights (India 2025)
- Demand index for 10 career domains
- Salary range charts (min/median/max) for 10 roles
- Top hiring companies with role counts
- Hiring city distribution (pie chart)
- YoY growth forecast
- Placement rates by institution type

### 5.7 Progress Dashboard
- Profile completion KPI bar
- Milestone tracker with checkboxes (interactive)
- Skill portfolio donut chart
- Proficiency level distribution chart
- Career snapshot summary card

---

## 6. IBM watsonx.ai Integration Details

### 6.1 Model Used

**IBM Granite 13B Instruct v2** (`ibm/granite-13b-instruct-v2`)

- Parameters: 13 billion
- Type: Instruction-tuned decoder
- Specialties: Following complex instructions, structured output, conversational tasks
- Availability: IBM watsonx.ai (free tier available)

### 6.2 Generation Parameters

```python
GRANITE_PARAMS = {
    "max_new_tokens": 800,
    "min_new_tokens": 20,
    "temperature": 0.7,       # Balanced creativity
    "top_p": 0.9,             # Nucleus sampling
    "repetition_penalty": 1.1 # Reduce repetition
}
```

### 6.3 Prompt Design

Each agent uses a specialised instruction prompt:

**Career Counselor Prompt:**
```
System: You are CareerMitra, an experienced AI career counselor...
Student Profile: [injected from database]
Conversation: [last 6 turns]
Student: [current question]
CareerMitra:
```

**Skill Gap Prompt:**
```
Analyse the skill gap for {domain}.
Current: {current_skills}
Required: {required_skills}
Missing: {missing_skills}
Provide actionable analysis in 3-5 bullet points...
```

### 6.4 Fallback / Demo Mode

When IBM credentials are absent, the system automatically uses pre-written domain-aware responses that:
- Feel natural and helpful
- Include real career data
- Clearly label themselves as demo responses
- Encourage users to add credentials

---

## 7. Testing

### 7.1 Functionality Testing

| Feature | Test | Result |
|---|---|---|
| Student Profile Save | Create profile with valid email | ✅ Stored in SQLite |
| Profile Update | Update existing profile by email | ✅ UPSERT works correctly |
| Skills Save | Select 5 skills with proficiency | ✅ Saved and retrieved |
| Interests Save | Select 3 interests | ✅ Saved and retrieved |
| Chat History | Send 3 messages, reload page | ✅ History persists in DB |
| Career Scoring | PCM + Coding → Tech domain | ✅ Scores as expected |
| Skill Gap Radar | Data Science domain, no skills | ✅ All gaps shown as 0% |
| Milestone Checkbox | Toggle complete/incomplete | ✅ DB updated immediately |
| Demo Mode | Run without IBM credentials | ✅ Demo responses displayed |

### 7.2 Python Syntax Validation

All source files pass `ast.parse()` without errors:

```
✅ app.py
✅ src/config.py
✅ src/database.py
✅ src/ibm_granite.py
✅ src/pages/home.py
✅ src/pages/student_profile.py
✅ src/pages/ai_counselor.py
✅ src/pages/career_recommendations.py
✅ src/pages/skill_gap.py
✅ src/pages/roadmap.py
✅ src/pages/job_market.py
✅ src/pages/dashboard.py
```

---

## 8. Limitations & Future Work

### 8.1 Current Limitations

- Job market data is static (2025 estimates) — not live API-fetched
- Career recommendation scoring is rule-based; a trained ML model would improve accuracy
- Single-user deployment (SQLite is not suited for concurrent multi-user production)
- IBM Granite requires an internet connection

### 8.2 Future Enhancements

| Enhancement | Priority | Effort |
|---|---|---|
| Live job scraping (Naukri, LinkedIn) | High | Medium |
| Resume parser and ATS score | High | High |
| ML-based career matching | Medium | High |
| PostgreSQL for multi-user production | Medium | Medium |
| Mock interview simulator | High | High |
| Multilingual support (Hindi) via Granite Multilingual | Medium | Low |
| Mobile-responsive UI | Low | Medium |

---

## 9. Conclusion

CareerMitra AI successfully demonstrates the application of IBM Granite LLM in a real-world educational guidance context. The system:

- **Solves a genuine problem** — career guidance access gap for Indian students
- **Uses IBM technology responsibly** — Granite 13B for contextual, personalised advice
- **Is fully functional** — 8 modules, 270+ lines of DB code, real chart data
- **Is production-ready in design** — modular `src/` architecture, `.env` credential management, demo mode fallback

The project establishes a foundation for a more comprehensive career guidance platform that can scale to serve thousands of students across India.

---

*CareerMitra AI — Empowering every student's career journey with IBM Granite intelligence.*
