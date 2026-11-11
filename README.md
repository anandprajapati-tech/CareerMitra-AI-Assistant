# CareerMitra AI Assistant

### Your Intelligent AI Career Companion — Discover Your Potential, Build Your Future.

> **IBM Granite · Streamlit · SQLite · Plotly · Pandas**

CareerMitra AI Assistant is a premium, AI-powered career guidance platform that helps students discover the right career, bridge skill gaps, and build a clear roadmap to success — powered by **IBM Granite LLM via IBM watsonx.ai**.

---

## 🚀 Features

| Module | Description |
|---|---|
| **🏠 Home Dashboard** | Premium AI dashboard with hero section, feature cards, and CTA buttons |
| **👤 Student Profile** | Capture education, skills, and interests with a multi-tab form |
| **🤖 AI Career Counselor** | IBM Granite-powered chat for personalised career advice |
| **🎯 Career Recommendations** | Premium visual cards with compatibility scores and growth data |
| **📊 Skill Gap Analysis** | Radar chart + IBM Granite insights on what to learn |
| **🗺️ Career Roadmap** | Phase-by-phase milestones + AI-generated personalised plans |
| **📈 Job Market Insights** | Salary benchmarks, demand trends, top hiring companies |
| **📄 Resume Analyzer** | AI-powered resume feedback, ATS optimisation, keyword gaps |
| **🎤 AI Interview Prep** | Domain questions, AI model answers, and mock interview mode |
| **📋 Progress Dashboard** | Milestone tracker, skill portfolio, KPI summary |
| **⚙️ Settings** | IBM watsonx.ai config, connection test, data management |
| **🗄️ Student Database** | Persistent SQLite storage for all student data |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI Framework | Streamlit 1.32+ |
| AI / LLM | IBM Granite 13B Instruct via IBM watsonx.ai |
| Database | SQLite (Python `sqlite3`) |
| Data Processing | Pandas, NumPy |
| Visualisation | Plotly |
| PDF Export | FPDF2 |
| Presentation | python-pptx |
| Language | Python 3.11+ |

---

## 📁 Project Structure

```
CAREERMITRA AI/
├── app.py                        # Main Streamlit entry point
├── requirements.txt              # Python dependencies
├── README.md                     # Documentation
├── .env.example                  # Environment variable template
├── project_report.md             # Full project report
│
├── src/
│   ├── __init__.py
│   ├── config.py                 # All config constants, IBM credentials
│   ├── database.py               # SQLite CRUD operations
│   ├── ibm_granite.py            # IBM Granite LLM integration + prompts
│   └── pages/
│       ├── home.py               # Landing page
│       ├── student_profile.py    # Student profile management
│       ├── ai_counselor.py       # IBM Granite chat counselor
│       ├── career_recommendations.py
│       ├── skill_gap.py          # Skill gap analysis
│       ├── roadmap.py            # Career roadmap generator
│       ├── job_market.py         # Job market insights
│       └── dashboard.py          # Progress dashboard
│
├── data/
│   ├── career_data.json          # Career domains reference data
│   └── careermitra.db            # SQLite database (auto-created)
│
└── docs/
    └── CareerMitra_AI_Presentation.pptx
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11+
- An IBM Cloud account (free tier available)
- IBM watsonx.ai project

### 1. Clone / download the project
```bash
cd "CAREERMITRA AI"
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure IBM watsonx.ai credentials
```bash
copy .env.example .env      # Windows
cp .env.example .env        # macOS/Linux
```
Edit `.env`:
```env
IBM_WATSONX_API_KEY=your_api_key_here
IBM_WATSONX_PROJECT_ID=your_project_id_here
IBM_WATSONX_URL=https://au-syd.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-13b-instruct-v2
```

> ⚠️ **Important — Project ID must match region:**
> IBM watsonx.ai projects are **region-specific**. If your Project ID was created
> in a different region (e.g. `us-south`), it will not be found on `au-syd`.
> Go to [https://dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com),
> create a new project in the **Sydney** region, and copy its Project ID into `.env`.

### 5. Run the application
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 🤖 IBM Granite Integration

CareerMitra AI uses **IBM Granite 13B Instruct** for:

1. **AI Career Counselor** — Personalised chat using student profile context
2. **Career Recommendations** — AI analysis of top-matched career paths
3. **Skill Gap Analysis** — Targeted learning recommendations for missing skills
4. **Career Roadmap** — Personalised milestone-based career plans

### Getting IBM watsonx.ai Credentials

1. Create a free account: [ibm.com/watsonx](https://www.ibm.com/watsonx)
2. Navigate to watsonx.ai → Create a project
3. Copy your **Project ID** from project settings
4. Go to IBM Cloud → Manage → Access (IAM) → API Keys → Create an API key
5. Add both to your `.env` file

### Supported Granite Models

| Model ID | Description |
|---|---|
| `ibm/granite-13b-instruct-v2` | Recommended — fast, instruction-tuned |
| `ibm/granite-20b-multilingual` | Multilingual support (Hindi, etc.) |

---

## 🏃 Demo Mode

If IBM credentials are not configured, CareerMitra AI runs in **Demo Mode**:
- All features work fully
- AI-powered modules return pre-written demo responses
- The demo badge is shown in the sidebar
- Add credentials any time to activate full AI

---

## 📊 Database Schema

The SQLite database (`data/careermitra.db`) contains:

| Table | Purpose |
|---|---|
| `students` | Student personal and education info |
| `student_skills` | Skills with proficiency levels |
| `student_interests` | Areas of interest |
| `career_goals` | Target domain, role, and timeline |
| `counselor_sessions` | Full chat history per student |
| `recommendations` | Saved AI career recommendations |
| `progress_milestones` | Learning milestones and completion |

---

## 📄 License

MIT License — Free for educational and personal use.

---

*Built with ❤️ — CareerMitra AI is powered by IBM Granite and designed for Indian students navigating their career journey.*
