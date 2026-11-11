# docs/generate_presentation.py
# CareerMitra AI – Generate PowerPoint Presentation
# Run: python docs/generate_presentation.py

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

# ── Color palette ──────────────────────────────────────────────────────────────
C_BG       = RGBColor(0x0F, 0x17, 0x2A)   # Dark navy
C_CARD     = RGBColor(0x1E, 0x29, 0x3B)   # Slate 800
C_PRIMARY  = RGBColor(0x4F, 0x46, 0xE5)   # Indigo
C_ACCENT   = RGBColor(0x06, 0xB6, 0xD4)   # Cyan
C_SUCCESS  = RGBColor(0x10, 0xB9, 0x81)   # Emerald
C_WARNING  = RGBColor(0xF5, 0x9E, 0x0B)   # Amber
C_WHITE    = RGBColor(0xF1, 0xF5, 0xF9)   # Slate 100
C_MUTED    = RGBColor(0x94, 0xA3, 0xB8)   # Slate 400
C_IBM      = RGBColor(0x00, 0x61, 0xFF)   # IBM Blue


def set_bg(slide, prs):
    """Set slide background to dark navy."""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = C_BG


def add_textbox(slide, text, left, top, width, height,
                font_size=18, bold=False, color=None, align=PP_ALIGN.LEFT, italic=False):
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color or C_WHITE
    return txBox


def add_rect(slide, left, top, width, height, fill_color, alpha=None):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    return shape


def add_accent_bar(slide, color=None):
    """Add a thin horizontal accent bar at top."""
    bar = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.33), Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = color or C_PRIMARY
    bar.line.fill.background()


def make_slide(prs, layout_idx=6):
    slide_layout = prs.slide_layouts[layout_idx]
    return prs.slides.add_slide(slide_layout)


# ── Slides ─────────────────────────────────────────────────────────────────────

def slide_title(prs):
    slide = make_slide(prs)
    set_bg(slide, prs)
    add_accent_bar(slide, C_IBM)

    # IBM badge
    badge = add_rect(slide, 0.4, 0.3, 2.2, 0.35, C_IBM)
    add_textbox(slide, "IBM watsonx.ai", 0.4, 0.3, 2.2, 0.35,
                font_size=10, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)

    # Main title
    add_textbox(slide, "🎓 CareerMitra AI", 0.5, 1.1, 12.3, 1.4,
                font_size=44, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    add_textbox(slide, "Agentic Career Counseling Companion", 0.5, 2.4, 12.3, 0.7,
                font_size=24, bold=False, color=C_ACCENT, align=PP_ALIGN.CENTER)
    add_textbox(slide, "Powered by IBM Granite · Streamlit · SQLite · Plotly · Pandas",
                0.5, 3.1, 12.3, 0.5, font_size=14, color=C_MUTED, align=PP_ALIGN.CENTER)

    # Divider line (thin rect)
    div = slide.shapes.add_shape(1, Inches(3.5), Inches(3.7), Inches(6.3), Inches(0.03))
    div.fill.solid()
    div.fill.fore_color.rgb = C_PRIMARY
    div.line.fill.background()

    # Tagline
    add_textbox(slide,
                "Helping every Indian student discover the right career path\n"
                "with AI-powered personalisation and real job market intelligence",
                0.5, 3.85, 12.3, 1.0, font_size=16, color=C_MUTED, align=PP_ALIGN.CENTER, italic=True)


def slide_problem(prs):
    slide = make_slide(prs)
    set_bg(slide, prs)
    add_accent_bar(slide, C_WARNING)

    add_textbox(slide, "⚠️ Problem Statement", 0.4, 0.2, 12.3, 0.6,
                font_size=28, bold=True, color=C_WHITE)

    problems = [
        ("45–60%",  "of graduates are misaligned with their career",   C_WARNING),
        ("3M+",     "engineering graduates every year in India",        C_ACCENT),
        ("No Access","to professional career counselors in tier-2/3 cities", C_PRIMARY),
        ("Generic", "advice that ignores individual skills and interests", C_SUCCESS),
    ]
    for i, (stat, desc, color) in enumerate(problems):
        col = i % 2
        row = i // 2
        x = 0.4 + col * 6.5
        y = 1.1 + row * 2.1
        box = add_rect(slide, x, y, 6.0, 1.7, C_CARD)
        add_textbox(slide, stat, x + 0.2, y + 0.1, 5.6, 0.7,
                    font_size=32, bold=True, color=color)
        add_textbox(slide, desc, x + 0.2, y + 0.75, 5.6, 0.75,
                    font_size=14, color=C_MUTED)

    add_textbox(slide, "CareerMitra AI solves this with IBM Granite-powered personalised guidance.",
                0.4, 5.0, 12.3, 0.45, font_size=14, color=C_SUCCESS, italic=True)


def slide_solution(prs):
    slide = make_slide(prs)
    set_bg(slide, prs)
    add_accent_bar(slide, C_SUCCESS)

    add_textbox(slide, "💡 Our Solution", 0.4, 0.2, 12.3, 0.6,
                font_size=28, bold=True, color=C_WHITE)

    add_textbox(slide,
                "CareerMitra AI is a multi-agent, IBM Granite-powered career counseling application "
                "that provides 24/7 personalised guidance to students — completely free.",
                0.4, 0.85, 12.3, 0.8, font_size=16, color=C_MUTED)

    features = [
        ("👤", "Student Profile",          "Education, skills, interests"),
        ("🤖", "AI Counselor",             "IBM Granite chat advisor"),
        ("🎯", "Career Recommendations",   "AI-matched paths + scores"),
        ("📊", "Skill Gap Analysis",       "Radar chart + AI insights"),
        ("🗺️", "Career Roadmap",           "Phase-based milestone plan"),
        ("📈", "Job Market Insights",      "Salary & demand data"),
    ]
    for i, (icon, title, desc) in enumerate(features):
        col = i % 3
        row = i // 3
        x = 0.35 + col * 4.35
        y = 1.9 + row * 1.8
        add_rect(slide, x, y, 4.05, 1.55, C_CARD)
        add_textbox(slide, icon,  x + 0.15, y + 0.1,  0.6,  0.5, font_size=22)
        add_textbox(slide, title, x + 0.75, y + 0.12, 3.1,  0.45, font_size=13, bold=True)
        add_textbox(slide, desc,  x + 0.15, y + 0.75, 3.7,  0.5, font_size=11, color=C_MUTED)


def slide_tech_stack(prs):
    slide = make_slide(prs)
    set_bg(slide, prs)
    add_accent_bar(slide, C_IBM)

    add_textbox(slide, "🛠️ Technology Stack", 0.4, 0.2, 12.3, 0.6,
                font_size=28, bold=True, color=C_WHITE)

    stack = [
        ("IBM Granite 13B",   "ibm/granite-13b-instruct-v2 via watsonx.ai",  C_IBM),
        ("Streamlit",         "Web UI framework — Python-native, zero JS",   C_PRIMARY),
        ("SQLite",            "Embedded database — zero config, persistent",  C_ACCENT),
        ("Plotly",            "Interactive charts, dark-theme visualisation", C_SUCCESS),
        ("Pandas + NumPy",    "Data processing and scoring algorithms",       C_WARNING),
        ("python-dotenv",     "Secure credential management via .env",        C_MUTED),
    ]
    for i, (tech, desc, color) in enumerate(stack):
        y = 1.0 + i * 0.73
        add_rect(slide, 0.4, y, 12.5, 0.62, C_CARD)
        bar = slide.shapes.add_shape(1, Inches(0.4), Inches(y), Inches(0.07), Inches(0.62))
        bar.fill.solid(); bar.fill.fore_color.rgb = color; bar.line.fill.background()
        add_textbox(slide, tech, 0.6, y + 0.02, 3.0, 0.55, font_size=14, bold=True, color=color)
        add_textbox(slide, desc, 3.7, y + 0.06, 9.0, 0.45, font_size=12, color=C_MUTED)


def slide_ibm_granite(prs):
    slide = make_slide(prs)
    set_bg(slide, prs)
    add_accent_bar(slide, C_IBM)

    add_textbox(slide, "🤖 IBM Granite Integration", 0.4, 0.2, 12.3, 0.6,
                font_size=28, bold=True, color=C_WHITE)

    # Left: how it works
    add_rect(slide, 0.4, 1.0, 6.0, 4.5, C_CARD)
    add_textbox(slide, "How IBM Granite Powers CareerMitra", 0.6, 1.05, 5.6, 0.5,
                font_size=14, bold=True, color=C_IBM)
    steps = [
        "1. Student profile stored in SQLite",
        "2. Profile context injected into Granite prompt",
        "3. Granite 13B generates personalised response",
        "4. Response displayed in Streamlit chat UI",
        "5. History maintained across sessions",
    ]
    for i, s in enumerate(steps):
        add_textbox(slide, s, 0.6, 1.65 + i * 0.55, 5.6, 0.45, font_size=12, color=C_WHITE)

    # Right: prompt example
    add_rect(slide, 6.8, 1.0, 6.1, 4.5, C_CARD)
    add_textbox(slide, "Prompt Architecture", 6.95, 1.05, 5.7, 0.5,
                font_size=14, bold=True, color=C_ACCENT)
    prompt_text = (
        'System: "You are CareerMitra, an AI\n'
        '   career counselor for Indian students..."\n\n'
        'Student Profile:\n'
        '  Name: Arjun | Age: 20 | City: Pune\n'
        '  Education: B.Tech CS | GPA: 8.5\n'
        '  Skills: Python, SQL, ML\n'
        '  Goal: Data Science & AI/ML\n\n'
        'Student: "What certifications should\n'
        '   I prioritise this year?"\n\n'
        'CareerMitra: [Granite generates response]'
    )
    add_textbox(slide, prompt_text, 6.95, 1.65, 5.7, 3.6,
                font_size=10, color=C_MUTED, italic=True)

    add_textbox(slide, "Fallback Demo Mode: Pre-written domain-aware responses when credentials are absent.",
                0.4, 5.6, 12.5, 0.4, font_size=11, color=C_SUCCESS, italic=True)


def slide_architecture(prs):
    slide = make_slide(prs)
    set_bg(slide, prs)
    add_accent_bar(slide, C_ACCENT)

    add_textbox(slide, "🏗️ System Architecture", 0.4, 0.2, 12.3, 0.6,
                font_size=28, bold=True, color=C_WHITE)

    # Layers
    layers = [
        ("Streamlit UI Layer",   "8 Pages: Home, Profile, Counselor, Recommendations, Skill Gap, Roadmap, Job Market, Dashboard", C_PRIMARY),
        ("Agent / Business Logic", "src/pages/*.py — 8 specialised agent modules",  C_ACCENT),
        ("IBM Granite Layer",    "src/ibm_granite.py — ModelInference SDK, prompt templates, fallback responses", C_IBM),
        ("Data Layer",           "src/database.py — SQLite CRUD (7 tables) | data/career_data.json — static data", C_SUCCESS),
    ]
    for i, (layer, desc, color) in enumerate(layers):
        y = 1.1 + i * 1.1
        add_rect(slide, 0.4, y, 12.5, 0.9, C_CARD)
        bar = slide.shapes.add_shape(1, Inches(0.4), Inches(y), Inches(0.1), Inches(0.9))
        bar.fill.solid(); bar.fill.fore_color.rgb = color; bar.line.fill.background()
        add_textbox(slide, layer, 0.65, y + 0.06, 3.5, 0.4, font_size=13, bold=True, color=color)
        add_textbox(slide, desc,  4.2,  y + 0.1,  8.5, 0.65, font_size=11, color=C_MUTED)

    # Config block
    add_textbox(slide, "Configuration: src/config.py — IBM credentials, CAREER_DOMAINS, SKILL_CATEGORIES, UI theme colors",
                0.4, 5.55, 12.5, 0.45, font_size=11, color=C_WARNING)


def slide_features_deep(prs):
    slide = make_slide(prs)
    set_bg(slide, prs)
    add_accent_bar(slide, C_SUCCESS)

    add_textbox(slide, "📊 Key Feature Deep-Dives", 0.4, 0.2, 12.3, 0.6,
                font_size=28, bold=True, color=C_WHITE)

    features = [
        ("Skill Gap Analysis",
         "• Radar chart: current vs required proficiency\n"
         "• 8 career domains × 4–6 required skills\n"
         "• IBM Granite AI: actionable gap advice\n"
         "• Auto-generate milestones from gaps",
         C_PRIMARY),
        ("Career Recommendations",
         "• Scoring: Skills (45%) + Interests (35%) + Stream (20%)\n"
         "• Top 3 with match %, demand badge, salary\n"
         "• IBM Granite narrative analysis on demand\n"
         "• Domain deep-dive: roles, companies, education",
         C_ACCENT),
        ("Career Roadmap",
         "• 4-domain templates with phase-based milestones\n"
         "• IBM Granite personalised roadmap generation\n"
         "• Goal saving: domain, role, timeline, notes\n"
         "• Expandable phase cards (4 phases × 4 milestones)",
         C_SUCCESS),
        ("Progress Dashboard",
         "• Profile completion KPI bar (5 sections)\n"
         "• Interactive milestone tracker (check/uncheck)\n"
         "• Skill portfolio donut + proficiency bar chart\n"
         "• Career snapshot summary card",
         C_WARNING),
    ]
    for i, (title, content, color) in enumerate(features):
        col = i % 2
        row = i // 2
        x = 0.35 + col * 6.5
        y = 1.0 + row * 2.5
        add_rect(slide, x, y, 6.1, 2.25, C_CARD)
        bar = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(6.1), Inches(0.06))
        bar.fill.solid(); bar.fill.fore_color.rgb = color; bar.line.fill.background()
        add_textbox(slide, title,   x + 0.15, y + 0.1,  5.7, 0.45, font_size=14, bold=True, color=color)
        add_textbox(slide, content, x + 0.15, y + 0.55, 5.7, 1.55, font_size=10.5, color=C_MUTED)


def slide_job_market(prs):
    slide = make_slide(prs)
    set_bg(slide, prs)
    add_accent_bar(slide, C_WARNING)

    add_textbox(slide, "📈 Job Market Insights Module", 0.4, 0.2, 12.3, 0.6,
                font_size=28, bold=True, color=C_WHITE)

    data_items = [
        ("Career Demand Index",    "10 domains scored 0–100 (AI/ML: 92, Cloud: 88, Cybersecurity: 85)", C_SUCCESS),
        ("Salary Benchmarks",      "10 roles with min/median/max CTC in INR (Data Scientist: ₹8L–₹30L)", C_ACCENT),
        ("Top Hiring Companies",   "10 companies with open roles: TCS 18K, Amazon 3.2K, Google 1.2K",    C_PRIMARY),
        ("Top Hiring Cities",      "Bengaluru 28%, Hyderabad 18%, Mumbai 16%, Pune 12%, Chennai 10%",     C_WARNING),
        ("Skill Demand 2025",      "GenAI/LLMs: 95%, Python: 90%, Cloud: 88%, Prompt Engineering: 85%",  C_IBM),
        ("Growth Forecast YoY",    "AI/ML: +45%, Cloud: +32%, Cybersecurity: +28%, FinTech: +25%",       C_SUCCESS),
        ("Fresher Placement Rates","IIM: 99%, IIT: 96%, NIT: 88%, B.Sc/B.Com: 42%",                     C_MUTED),
    ]
    for i, (label, value, color) in enumerate(data_items):
        y = 1.0 + i * 0.68
        add_rect(slide, 0.4, y, 12.5, 0.58, C_CARD)
        dot = slide.shapes.add_shape(1, Inches(0.55), Inches(y + 0.2), Inches(0.15), Inches(0.15))
        dot.fill.solid(); dot.fill.fore_color.rgb = color; dot.line.fill.background()
        add_textbox(slide, label, 0.85, y + 0.05, 3.5, 0.45, font_size=12, bold=True, color=color)
        add_textbox(slide, value, 4.4,  y + 0.07, 8.3, 0.4, font_size=11, color=C_MUTED)


def slide_demo_flow(prs):
    slide = make_slide(prs)
    set_bg(slide, prs)
    add_accent_bar(slide, C_PRIMARY)

    add_textbox(slide, "🚀 User Journey", 0.4, 0.2, 12.3, 0.6,
                font_size=28, bold=True, color=C_WHITE)

    steps = [
        ("1", "Create Profile",          "Name, email, education, stream, city, GPA",              C_PRIMARY),
        ("2", "Add Skills & Interests",  "50+ skills across 4 categories, 15 interest areas",       C_ACCENT),
        ("3", "Get Recommendations",     "AI-scored career paths with demand + salary insights",     C_SUCCESS),
        ("4", "Analyse Skill Gaps",      "Radar chart: current vs required + IBM Granite advice",    C_WARNING),
        ("5", "Build Career Roadmap",    "Set target role → 4-phase milestone plan + AI roadmap",    C_IBM),
        ("6", "Chat with AI Counselor",  "IBM Granite conversation with full profile context",       C_PRIMARY),
        ("7", "Track Progress",          "Tick off milestones, review skill portfolio, check KPIs",  C_SUCCESS),
    ]
    for i, (num, title, desc, color) in enumerate(steps):
        y = 1.05 + i * 0.73
        add_rect(slide, 0.4, y, 12.5, 0.62, C_CARD)
        badge = add_rect(slide, 0.45, y + 0.06, 0.5, 0.5, color)
        add_textbox(slide, num,   0.45, y + 0.08, 0.5, 0.45, font_size=14, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
        add_textbox(slide, title, 1.1,  y + 0.07, 3.5, 0.45, font_size=13, bold=True, color=color)
        add_textbox(slide, desc,  4.7,  y + 0.1,  7.9, 0.4, font_size=11, color=C_MUTED)


def slide_limitations_future(prs):
    slide = make_slide(prs)
    set_bg(slide, prs)
    add_accent_bar(slide, C_MUTED)

    add_textbox(slide, "🔭 Limitations & Future Work", 0.4, 0.2, 12.3, 0.6,
                font_size=28, bold=True, color=C_WHITE)

    # Limitations
    add_rect(slide, 0.4, 1.0, 5.8, 4.5, C_CARD)
    add_textbox(slide, "⚠️ Current Limitations", 0.55, 1.05, 5.4, 0.45, font_size=14, bold=True, color=C_WARNING)
    limits = [
        "Job market data is static (2025 estimates)",
        "Scoring is rule-based, not ML-trained",
        "SQLite: single-user, not multi-tenant",
        "Requires internet for IBM Granite",
        "No resume parsing or ATS scoring yet",
    ]
    for i, lim in enumerate(limits):
        add_textbox(slide, f"• {lim}", 0.55, 1.6 + i * 0.58, 5.4, 0.48, font_size=12, color=C_MUTED)

    # Future
    add_rect(slide, 6.6, 1.0, 6.0, 4.5, C_CARD)
    add_textbox(slide, "🚀 Future Enhancements", 6.75, 1.05, 5.6, 0.45, font_size=14, bold=True, color=C_SUCCESS)
    futures = [
        "Live job scraping (Naukri, LinkedIn API)",
        "Resume parser + ATS compatibility score",
        "ML-based career matching (trained model)",
        "Mock interview simulator with AI feedback",
        "Hindi support via Granite Multilingual",
        "PostgreSQL for production deployment",
    ]
    for i, fut in enumerate(futures):
        add_textbox(slide, f"• {fut}", 6.75, 1.6 + i * 0.58, 5.6, 0.48, font_size=12, color=C_MUTED)

    add_textbox(slide, "The current version is a strong MVP demonstrating real IBM Granite value in career guidance.",
                0.4, 5.6, 12.5, 0.4, font_size=12, color=C_SUCCESS, italic=True, align=PP_ALIGN.CENTER)


def slide_conclusion(prs):
    slide = make_slide(prs)
    set_bg(slide, prs)
    add_accent_bar(slide, C_IBM)

    add_textbox(slide, "✅ Conclusion", 0.4, 0.3, 12.3, 0.6,
                font_size=28, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)

    add_textbox(slide,
                "CareerMitra AI successfully demonstrates IBM Granite's capability\n"
                "in a real-world educational guidance application.",
                0.4, 1.0, 12.3, 0.9, font_size=18, color=C_MUTED, align=PP_ALIGN.CENTER, italic=True)

    achievements = [
        ("8 Modules",         "Complete multi-agent career guidance system",  C_PRIMARY),
        ("IBM Granite",       "4 AI-powered features using watsonx.ai SDK",   C_IBM),
        ("270+ DB lines",     "Robust SQLite schema with 7 tables",           C_ACCENT),
        ("Demo Mode",         "Fully functional without IBM credentials",      C_SUCCESS),
        ("Real Data",         "India 2025 job market data, salaries, trends", C_WARNING),
        ("Production-Ready",  "Modular src/ architecture, .env management",   C_SUCCESS),
    ]
    for i, (stat, desc, color) in enumerate(achievements):
        col = i % 3
        row = i // 3
        x = 0.35 + col * 4.35
        y = 2.2 + row * 1.6
        add_rect(slide, x, y, 4.05, 1.35, C_CARD)
        bar = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(4.05), Inches(0.05))
        bar.fill.solid(); bar.fill.fore_color.rgb = color; bar.line.fill.background()
        add_textbox(slide, stat, x + 0.15, y + 0.1,  3.7, 0.5, font_size=16, bold=True, color=color)
        add_textbox(slide, desc, x + 0.15, y + 0.65, 3.7, 0.55, font_size=11, color=C_MUTED)

    add_textbox(slide,
                "🎓 CareerMitra AI — Empowering every student's career journey with IBM Granite intelligence",
                0.4, 5.55, 12.5, 0.45, font_size=13, color=C_WHITE,
                bold=True, align=PP_ALIGN.CENTER)


# ── Main ───────────────────────────────────────────────────────────────────────

def generate():
    prs = Presentation()
    prs.slide_width  = Inches(13.33)
    prs.slide_height = Inches(7.5)

    slide_title(prs)
    slide_problem(prs)
    slide_solution(prs)
    slide_tech_stack(prs)
    slide_ibm_granite(prs)
    slide_architecture(prs)
    slide_features_deep(prs)
    slide_job_market(prs)
    slide_demo_flow(prs)
    slide_limitations_future(prs)
    slide_conclusion(prs)

    os.makedirs("docs", exist_ok=True)
    output_path = os.path.join("docs", "CareerMitra_AI_Presentation.pptx")
    prs.save(output_path)
    print("[OK] Presentation saved: " + output_path)
    print("     Slides: " + str(len(prs.slides)))
    return output_path


if __name__ == "__main__":
    generate()
