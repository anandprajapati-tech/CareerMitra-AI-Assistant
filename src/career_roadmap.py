# src/career_roadmap.py
# CareerMitra AI – Career Roadmap Data & Logic
# Provides structured roadmap templates and helpers; pages render these.

from __future__ import annotations

# ── Roadmap template data ─────────────────────────────────────────────────────

ROADMAP_TEMPLATES: dict[str, list[dict]] = {
    "Technology & Engineering": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Learn Python / Java fundamentals — freeCodeCamp or CS50",
            "Complete Data Structures & Algorithms basics",
            "Set up GitHub profile and commit daily",
            "Build 2 small projects (calculator, to-do app)",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Study Operating Systems, Networks, and Databases",
            "Learn SQL and build database-backed applications",
            "Solve 150+ LeetCode problems (Easy → Medium)",
            "Contribute to 1 open-source project",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Choose: Backend, DevOps, Cloud, or Embedded track",
            "Earn AWS / GCP / Azure Cloud Foundation certification",
            "Build a full-stack capstone project",
            "Apply for internships or entry-level roles",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Land a Software Engineer role at a target company",
            "Clear DSA + System Design interview rounds",
            "Build a professional network on LinkedIn (500+ connections)",
            "Plan advanced certifications within 2 years",
        ]},
    ],
    "Data Science & AI/ML": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Master Python (NumPy, Pandas, Matplotlib, Seaborn)",
            "Complete Andrew Ng's Machine Learning course on Coursera",
            "Learn Statistics & Probability fundamentals",
            "Participate in 2 beginner Kaggle competitions",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Learn SQL and practice data analysis on real datasets",
            "Study Deep Learning (CNNs, RNNs, Transformers)",
            "Build 3 portfolio projects on GitHub",
            "Earn Google Data Analytics or IBM Data Science certificate",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Specialise in NLP, Computer Vision, or MLOps",
            "Deploy ML models with FastAPI and Docker",
            "Learn cloud ML (AWS SageMaker or Vertex AI)",
            "Apply for Data Analyst / Junior Data Scientist roles",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Secure a Data Scientist or ML Engineer position",
            "Contribute to published research or write a technical blog",
            "Mentor junior data enthusiasts in your organisation",
            "Explore advanced certifications (TensorFlow, Databricks)",
        ]},
    ],
    "Business & Management": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Learn core business concepts (marketing, finance, operations)",
            "Master Excel and basic financial modelling",
            "Read business classics: Good to Great, Zero to One",
            "Join a case study club or debate team",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Learn project management (Agile / Scrum basics)",
            "Build Power BI or Tableau data visualisation skills",
            "Complete an internship in a business function",
            "Grow your LinkedIn network to 200+ connections",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Prepare for CAT / GMAT for MBA admission",
            "Choose a track: Consulting, Product, or Operations",
            "Complete a strategy internship at a firm",
            "Earn PMP or CAPM project management certification",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Join a top MBA programme or management trainee scheme",
            "Land an Analyst role at a consulting / product firm",
            "Lead a cross-functional project",
            "Build executive presence through thought leadership",
        ]},
    ],
    "Finance & Accounting": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Learn accounting basics: P&L, Balance Sheet, Cash Flow",
            "Master Excel (VLOOKUP, Pivot Tables, Macros)",
            "Start CA Foundation / CFA Level 1 preparation",
            "Open a Demat account and study the stock market",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Complete CA Intermediate / CFA Level 1",
            "Build financial models in Excel",
            "Intern at a CA firm, bank, or NBFC",
            "Learn Tally, QuickBooks, or SAP basics",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Clear CA Final / CFA Level 2",
            "Choose a track: Audit, Tax, IB, or Corporate Finance",
            "Build ICAI / CFA community network",
            "Complete MBA Finance if targeting investment banking",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Join a Big 4 firm, bank, or hedge fund",
            "Obtain full CA / CFA / CPA designation",
            "Manage a financial portfolio or audit team",
            "Chart a path toward CFO / senior finance track",
        ]},
    ],
    "Healthcare & Medicine": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Strengthen Biology, Chemistry, and Physics fundamentals",
            "Prepare for NEET / medical entrance examinations",
            "Shadow a doctor or healthcare professional for 4 weeks",
            "Join pre-medical volunteer programmes",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Enrol in MBBS / BPharm / Nursing programme",
            "Learn clinical research basics and data analysis",
            "Attend healthcare seminars and webinars",
            "Intern or volunteer at a local hospital",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Choose a medical speciality or healthcare track",
            "Complete mandatory clinical rotations",
            "Study for USMLE / DNB / postgraduate entrance exams",
            "Build a research publication or case study",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Complete residency / MD / specialist training",
            "Register with NMC and obtain your medical licence",
            "Join a government or private hospital / clinic",
            "Pursue higher speciality or healthcare management MBA",
        ]},
    ],
    "Creative Arts & Design": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Learn design fundamentals: typography, colour, composition",
            "Master Figma (UI/UX) or Adobe Suite (Graphic Design)",
            "Build a personal portfolio of 5 beginner projects",
            "Study successful design case studies",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Complete Google UX Design Certificate on Coursera",
            "Learn basic user research and usability testing",
            "Redesign an existing app or website as a portfolio project",
            "Grow your Behance / Dribbble profile",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Choose a track: UX/UI, Motion, Branding, or Game Design",
            "Complete a design internship",
            "Contribute to open-source design systems",
            "Attend design hackathons and critique sessions",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Land a UX Designer / Graphic Designer role",
            "Build a strong client portfolio or agency experience",
            "Mentor junior designers and contribute to design community",
            "Explore freelance or startup design leadership",
        ]},
    ],
    "Education & Research": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Strengthen subject-matter expertise in your field",
            "Learn academic writing and research methodology",
            "Identify target universities or research labs",
            "Write and publish your first blog or article",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Complete a Master's programme or research fellowship",
            "Co-author a research paper with a senior mentor",
            "Learn statistical tools: R, SPSS, or STATA",
            "Present at a student seminar or conference",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Begin PhD or postdoctoral research",
            "Publish in a peer-reviewed journal",
            "Apply for research grants (DST, UGC, or international)",
            "Build collaborations with international researchers",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Secure a lecturer, researcher, or scientist position",
            "Build a citation record and research portfolio",
            "Supervise junior researchers or students",
            "Pursue tenure-track or senior research roles",
        ]},
    ],
    "Sales & Marketing": [
        {"phase": "Foundation (0–6 months)", "milestones": [
            "Learn marketing fundamentals: 4Ps, consumer psychology",
            "Complete Google Digital Marketing Certificate",
            "Set up and run a personal social media brand",
            "Read: Influence (Cialdini), This Is Marketing (Godin)",
        ]},
        {"phase": "Skill Building (6–18 months)", "milestones": [
            "Learn SEO, SEM, email marketing, and analytics",
            "Complete an internship at a marketing agency or brand",
            "Build campaigns that generate measurable results",
            "Earn HubSpot or Facebook Blueprint certification",
        ]},
        {"phase": "Specialisation (18–30 months)", "milestones": [
            "Choose a track: Digital, Brand, Sales, or Growth",
            "Run a full-funnel marketing campaign independently",
            "Develop public speaking and presentation skills",
            "Build a network of 300+ industry contacts",
        ]},
        {"phase": "Career Launch (30+ months)", "milestones": [
            "Join a leading brand, agency, or startup",
            "Own a P&L or marketing budget",
            "Pursue MBA Marketing for leadership track",
            "Build your personal brand as a marketing thought leader",
        ]},
    ],
}

DEFAULT_ROADMAP: list[dict] = [
    {"phase": "Foundation (0–6 months)", "milestones": [
        "Research the field and identify 3 key sub-domains",
        "Take a foundational course on Coursera, edX, or YouTube",
        "Connect with 5 professionals in your field on LinkedIn",
        "Set SMART short-term and long-term career goals",
    ]},
    {"phase": "Skill Building (6–18 months)", "milestones": [
        "Complete 2 relevant industry certifications",
        "Build a portfolio or proof-of-work project",
        "Attend industry events or virtual webinars",
        "Find a mentor in your target field",
    ]},
    {"phase": "Specialisation (18–30 months)", "milestones": [
        "Narrow focus to a high-demand sub-specialisation",
        "Complete an internship or part-time role",
        "Contribute to a community or publish content",
        "Apply for full-time roles or advanced programmes",
    ]},
    {"phase": "Career Launch (30+ months)", "milestones": [
        "Secure an entry-to-mid level role in your domain",
        "Build reputation through quality work and networking",
        "Plan for the next seniority level",
        "Give back by mentoring the next generation",
    ]},
]


def get_roadmap(domain: str) -> list[dict]:
    """Return the roadmap phases for *domain*, falling back to DEFAULT_ROADMAP."""
    return ROADMAP_TEMPLATES.get(domain, DEFAULT_ROADMAP)


def available_domains() -> list[str]:
    """Return all domains that have a dedicated roadmap template."""
    return list(ROADMAP_TEMPLATES.keys())


def get_phase_milestones(domain: str, phase_index: int) -> list[str]:
    """Return milestones for a specific phase (0-based index)."""
    roadmap = get_roadmap(domain)
    if 0 <= phase_index < len(roadmap):
        return roadmap[phase_index]["milestones"]
    return []
