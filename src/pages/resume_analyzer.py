# src/pages/resume_analyzer.py
# CareerMitra AI Assistant – Resume Analyzer (PDF / Image / Text upload)

from __future__ import annotations
import io
import warnings
import streamlit as st

from src.config import COLORS, ibm_configured
from src.database import get_student_by_id, get_career_goal
from src.ibm_granite import _get_model, get_model_error

warnings.filterwarnings("ignore", category=FutureWarning)   # fitz compat warning


# ══════════════════════════════════════════════════════════════════════════════
# Extraction helpers
# ══════════════════════════════════════════════════════════════════════════════

def _extract_pdf_text(file_bytes: bytes) -> tuple[str, str | None]:
    """
    Extract text from a PDF.
    Returns (extracted_text, warning_message_or_None).
    Uses PyMuPDF (fitz) as primary, pdfplumber as fallback.
    """
    text = ""
    warning = None

    # ── Primary: PyMuPDF ─────────────────────────────────────────────────────
    try:
        import fitz  # type: ignore  (pymupdf)
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text("text"))
        doc.close()
        text = "\n".join(pages_text).strip()
    except Exception as e:
        warning = f"PyMuPDF extraction issue: {e}. Trying fallback…"
        text = ""

    # ── Fallback: pdfplumber ─────────────────────────────────────────────────
    if len(text) < 30:
        try:
            import pdfplumber  # type: ignore
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages_text = []
                for page in pdf.pages:
                    pg = page.extract_text() or ""
                    pages_text.append(pg)
                text = "\n".join(pages_text).strip()
            warning = None  # pdfplumber succeeded; clear earlier warning
        except Exception as e:
            if warning:
                warning += f" pdfplumber also failed: {e}"
            else:
                warning = f"pdfplumber extraction error: {e}"

    # ── Detect scanned (image-only) PDF ──────────────────────────────────────
    if len(text) < 30:
        warning = (
            "⚠️ **Scanned / image-only PDF detected.**\n\n"
            "This PDF does not contain selectable text — it appears to be a scanned document. "
            "Please either:\n"
            "- Export a text-based version from Word/Google Docs\n"
            "- Take a clear photo of each page and use the **Image Upload** option below\n"
            "- Copy-paste the text manually into the text area"
        )

    return text, warning


def _extract_image_text(file_bytes: bytes, filename: str) -> tuple[str, str | None]:
    """
    Extract text from an image using OCR (pytesseract) if available,
    or return a graceful message if Tesseract is not installed.
    """
    warning = None

    # ── Check pytesseract + binary availability ───────────────────────────────
    try:
        import pytesseract  # type: ignore
        import shutil
        if not shutil.which("tesseract"):
            # Try common Windows install paths
            import os
            common_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
            for p in common_paths:
                if os.path.exists(p):
                    pytesseract.pytesseract.tesseract_cmd = p
                    break
            else:
                return "", (
                    "⚠️ **Tesseract OCR not found**\n\n"
                    "The `pytesseract` Python package is installed but the Tesseract executable "
                    "is not found on this system.\n\n"
                    "**To install Tesseract on Windows:**\n"
                    "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki\n"
                    "2. Run the installer (choose 'Add to PATH' during setup)\n"
                    "3. Restart the application\n\n"
                    "**Alternative:** Use the text area below to paste your resume text manually."
                )
    except ImportError:
        return "", (
            "⚠️ **OCR not available** (`pytesseract` not installed)\n\n"
            "Install it to enable image-based resume extraction:\n"
            "```\npip install pytesseract\n```\n"
            "You also need the Tesseract binary: "
            "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
            "**Alternative:** Paste your resume text manually in the text area."
        )

    # ── Run OCR ───────────────────────────────────────────────────────────────
    try:
        from PIL import Image, ImageFilter, ImageOps  # type: ignore

        img = Image.open(io.BytesIO(file_bytes))

        # Preprocessing for better OCR accuracy
        if img.mode != "RGB":
            img = img.convert("RGB")
        # Convert to grayscale → sharpen → threshold
        gray = ImageOps.grayscale(img)
        sharp = gray.filter(ImageFilter.SHARPEN)

        config = "--psm 6 --oem 3"   # Assume uniform block of text, LSTM engine
        text = pytesseract.image_to_string(sharp, config=config, lang="eng")
        text = text.strip()

        if len(text) < 20:
            warning = (
                "⚠️ OCR extracted very little text. "
                "Ensure the image is clear, well-lit, and not blurry. "
                "You can manually edit the extracted text below."
            )
        return text, warning
    except Exception as e:
        return "", f"⚠️ OCR error processing `{filename}`: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# AI Prompt builders  (preserved from original + enhanced)
# ══════════════════════════════════════════════════════════════════════════════

def _build_resume_prompt(resume_text: str, target_role: str, target_domain: str) -> str:
    return f"""You are an expert resume reviewer and career coach. Analyse the following resume for a candidate targeting the role of {target_role} in {target_domain}.

Resume:
{resume_text[:3500]}

Provide a structured, professional resume analysis covering ALL of the following sections:

1. **Overall Score** — Give a score out of 100 with a one-sentence justification. Note: this is an estimated ATS-compatibility and quality assessment, not an official ATS platform score.
2. **ATS Compatibility Score** — Estimate how well this resume would pass an Applicant Tracking System scan for the role of {target_role}. Score out of 100.
3. **Resume Strengths** — 3-4 specific strengths of this particular resume.
4. **Missing / Weak Skills** — Skills required for {target_role} in {target_domain} that are absent or underdeveloped.
5. **Missing Keywords** — Important ATS keywords for {target_role} that should be added.
6. **Education & Experience Feedback** — Quality and relevance of education and experience sections.
7. **Projects & Achievements** — How well projects demonstrate relevant impact; suggest improvements.
8. **Formatting & Structure** — Feedback on layout, length, section headers, bullet points.
9. **Top 5 Actionable Improvements** — Numbered list of the most impactful changes.
10. **Personalised Improvement Plan** — A 3-step plan tailored to this specific resume and target role.

Be specific, practical, honest, and encouraging.
Analysis:"""


def _build_generic_resume_prompt(resume_text: str) -> str:
    return f"""You are an expert resume reviewer. Analyse the following resume and provide comprehensive feedback.

Resume:
{resume_text[:3500]}

Provide a detailed analysis covering:
1. **Overall Score** (out of 100) — be realistic; this is an estimated quality and ATS-compatibility score.
2. **ATS Compatibility Score** (out of 100) — estimate how well this passes automated screening.
3. **Key Strengths** — what this resume does well (be specific).
4. **Critical Improvements** — specific changes to make immediately.
5. **Missing Keywords** — important industry keywords not present.
6. **Section-by-Section Feedback** — evaluate Summary, Experience, Skills, Education, Projects.
7. **Formatting Recommendations** — layout, length, structure issues.
8. **Top 5 Actionable Improvements** — numbered priority list.
9. **Next Steps** — a brief personalised improvement plan.

Be specific, actionable, and constructive.
Analysis:"""


def _demo_resume_analysis(resume_text: str) -> str:
    """Fallback analysis when IBM credentials are not configured."""
    word_count  = len(resume_text.split())
    has_email   = "@" in resume_text
    has_phone   = any(c.isdigit() for c in resume_text)
    has_github  = "github" in resume_text.lower()
    has_linkedin = "linkedin" in resume_text.lower()
    score = (55 + (5 if has_email else 0) + (5 if has_phone else 0) +
             (5 if has_github else 0) + (5 if has_linkedin else 0) +
             (5 if word_count > 200 else 0) + (5 if word_count < 700 else 0))

    return f"""**📊 Overall Score: {score}/100** *(estimated — connect IBM watsonx.ai for full AI analysis)*

**✅ Resume Strengths:**
• Word count: {word_count} — {'good length' if 200 < word_count < 700 else 'consider adjusting to 400–600 words'}
• {'✓ Contact email found' if has_email else '✗ Add your email address prominently'}
• {'✓ GitHub profile linked — excellent for tech roles' if has_github else '✗ Add GitHub/portfolio link (strongly recommended for tech roles)'}
• {'✓ LinkedIn profile included' if has_linkedin else '✗ Add LinkedIn URL for recruiter visibility'}

**⚠️ Areas to Improve:**
• Quantify achievements — use numbers, percentages, and impact metrics
• Start every bullet with a strong action verb (Led, Built, Designed, Reduced, Increased)
• Add a 2–3 line professional summary at the very top
• Tailor the skills section to exactly match target job description keywords

**🔍 ATS Keywords to Consider:**
Python, SQL, Machine Learning, Cloud Computing, Agile, Communication, Data Analysis, Project Management
*(Adjust based on your specific target role)*

**📐 Format & Structure:**
• 1 page for freshers/students · 2 pages for 3+ years experience
• Consistent font (Calibri or Arial, 11–12pt body, 14–16pt name)
• Balanced white space — avoid dense walls of text

**🚀 Top 3 Immediate Actions:**
1. Write a tailored 3-sentence professional summary at the top
2. Add measurable results to at least 3 bullet points
3. Mirror exact keywords from your target job description

*⚡ Connect IBM watsonx.ai credentials in your `.env` file for a fully personalised AI analysis.*"""


# ══════════════════════════════════════════════════════════════════════════════
# Resume statistics helper
# ══════════════════════════════════════════════════════════════════════════════

def _render_stats(resume_text: str):
    word_count = len(resume_text.split())
    char_count = len(resume_text)
    stats = [
        ("📝", "Words",       str(word_count),  "#4F46E5"),
        ("📊", "Characters",  str(char_count),  "#06B6D4"),
        ("📧", "Email",       "✓" if "@" in resume_text else "✗",
         "#10B981" if "@" in resume_text else "#EF4444"),
        ("🔗", "GitHub",      "✓" if "github" in resume_text.lower() else "✗",
         "#10B981" if "github" in resume_text.lower() else "#EF4444"),
    ]
    cols = st.columns(4)
    for col, (icon, label, val, color) in zip(cols, stats):
        with col:
            col_ = color
            st.markdown(
                f'<div style="background:#1E293B;border:1px solid #334155;border-left:3px solid {col_};'
                f'border-radius:8px;padding:0.75rem;text-align:center;">'
                f'<div style="font-size:1.2rem;">{icon}</div>'
                f'<div style="color:{col_};font-size:1.1rem;font-weight:700;">{val}</div>'
                f'<div style="color:#94A3B8;font-size:0.72rem;">{label}</div></div>',
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════════════════════════
# Main render function
# ══════════════════════════════════════════════════════════════════════════════

def render_resume_analyzer(student_id: int | None):
    st.markdown("## 📄 Resume Analyzer")
    st.markdown(
        "Upload your resume (PDF or image) or paste the text directly. "
        "Get AI-powered feedback on ATS compatibility, keyword gaps, and actionable improvements."
    )

    # ── IBM status badge ──────────────────────────────────────────────────────
    ibm_ok      = ibm_configured()
    model_error = get_model_error()
    sc = "#10B981" if ibm_ok and not model_error else ("#EF4444" if model_error else "#F59E0B")
    st_txt = ("IBM watsonx.ai Connected" if ibm_ok and not model_error else
              ("Configuration Error" if model_error else "Demo Mode — Add credentials for full AI analysis"))
    st.markdown(
        f'<div style="display:inline-flex;align-items:center;gap:0.5rem;background:#1E293B;'
        f'border:1px solid #334155;border-radius:20px;padding:0.3rem 0.85rem;'
        f'margin-bottom:0.75rem;font-size:0.8rem;">'
        f'<span style="width:8px;height:8px;border-radius:50%;background:{sc};display:inline-block;"></span>'
        f'<span style="color:{sc};">{st_txt}</span></div>',
        unsafe_allow_html=True,
    )
    if model_error and ibm_ok:
        with st.expander("⚠️ IBM Configuration Error", expanded=True):
            st.markdown(model_error)

    # ── Target role & domain ──────────────────────────────────────────────────
    goal    = get_career_goal(student_id)    if student_id else None
    student = get_student_by_id(student_id) if student_id else None

    rc1, rc2 = st.columns(2, gap="medium")
    with rc1:
        target_role = st.text_input(
            "🎯 Target Job Role:",
            value=goal.get("target_role", "") if goal else "",
            placeholder="e.g., Data Scientist, Software Engineer, Product Manager",
        )
    with rc2:
        target_domain = st.text_input(
            "🏢 Target Domain / Industry:",
            value=goal.get("goal_domain", "") if goal else "",
            placeholder="e.g., Data Science & AI/ML, Technology & Engineering",
        )

    st.markdown("---")

    # ── Input method selector ─────────────────────────────────────────────────
    st.markdown("### 📥 Choose How to Provide Your Resume")
    input_method = st.radio(
        label="Resume input method",
        options=[
            "📤 Upload PDF Resume",
            "🖼️ Upload Resume Image (JPG / PNG)",
            "📋 Paste Resume Text",
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="resume_input_method",
    )

    # Initialise session state for extracted text
    if "resume_extracted_text" not in st.session_state:
        st.session_state["resume_extracted_text"] = ""

    st.markdown("")   # spacer

    # ══════════════════════════════════════════════════════════════════════════
    # A) PDF Upload
    # ══════════════════════════════════════════════════════════════════════════
    if input_method == "📤 Upload PDF Resume":
        st.markdown("""
<div style="background:rgba(79,70,229,0.08);border:1px solid rgba(79,70,229,0.25);
            border-radius:10px;padding:0.75rem 1rem;margin-bottom:0.5rem;font-size:0.82rem;color:#94A3B8;">
    📌 <strong style="color:#E2E8F0;">Supported:</strong> Text-based PDFs exported from Word, Google Docs, or LaTeX.
    Scanned / image-only PDFs will be detected and you will be guided to use the Image Upload option instead.
</div>
""", unsafe_allow_html=True)

        uploaded_pdf = st.file_uploader(
            "Upload PDF Resume",
            type=["pdf"],
            key="pdf_uploader",
            label_visibility="collapsed",
            help="Upload a PDF resume. Max size: 10 MB.",
        )

        if uploaded_pdf is not None:
            file_size_kb = len(uploaded_pdf.getvalue()) // 1024
            st.markdown(
                f'<div style="background:#1E293B;border:1px solid #334155;border-radius:8px;'
                f'padding:0.6rem 1rem;margin:0.5rem 0;font-size:0.82rem;">'
                f'📄 <strong style="color:#E2E8F0;">{uploaded_pdf.name}</strong>'
                f'<span style="color:#94A3B8;margin-left:0.75rem;">{file_size_kb} KB · PDF</span></div>',
                unsafe_allow_html=True,
            )

            if st.button("📖 Extract Text from PDF", use_container_width=True, key="extract_pdf_btn"):
                with st.spinner("Extracting text from PDF…"):
                    pdf_bytes = uploaded_pdf.getvalue()
                    extracted, warn = _extract_pdf_text(pdf_bytes)

                if warn and len(extracted) < 30:
                    st.warning(warn)
                else:
                    if warn:
                        st.info(f"ℹ️ {warn}")
                    st.session_state["resume_extracted_text"] = extracted
                    st.success(
                        f"✅ Extracted {len(extracted.split())} words from "
                        f"{uploaded_pdf.name}. Review and edit below before analysing."
                    )

    # ══════════════════════════════════════════════════════════════════════════
    # B) Image Upload
    # ══════════════════════════════════════════════════════════════════════════
    elif input_method == "🖼️ Upload Resume Image (JPG / PNG)":
        st.markdown("""
<div style="background:rgba(79,70,229,0.08);border:1px solid rgba(79,70,229,0.25);
            border-radius:10px;padding:0.75rem 1rem;margin-bottom:0.5rem;font-size:0.82rem;color:#94A3B8;">
    📌 <strong style="color:#E2E8F0;">Tips for best results:</strong>
    Use a clear, well-lit photo or scan at 150+ DPI.
    Ensure text is readable and the image is not rotated.
    OCR requires <strong style="color:#E2E8F0;">Tesseract</strong> to be installed on this system.
</div>
""", unsafe_allow_html=True)

        uploaded_img = st.file_uploader(
            "Upload Resume Image",
            type=["jpg", "jpeg", "png"],
            key="img_uploader",
            label_visibility="collapsed",
            help="Upload JPG or PNG image of your resume.",
        )

        if uploaded_img is not None:
            file_size_kb = len(uploaded_img.getvalue()) // 1024
            # Show thumbnail preview
            try:
                from PIL import Image as PILImage
                thumb = PILImage.open(io.BytesIO(uploaded_img.getvalue()))
                thumb.thumbnail((320, 450))
                pcol1, pcol2 = st.columns([1, 2])
                with pcol1:
                    st.image(thumb, caption=f"{uploaded_img.name} ({file_size_kb} KB)", use_container_width=True)
                with pcol2:
                    st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:8px;padding:1rem;">
    <div style="color:#94A3B8;font-size:0.78rem;margin-bottom:0.3rem;">FILE DETAILS</div>
    <div style="color:#E2E8F0;font-weight:600;">{uploaded_img.name}</div>
    <div style="color:#94A3B8;font-size:0.8rem;margin-top:0.25rem;">
        Size: {file_size_kb} KB<br>
        Dimensions: {thumb.width * (thumb.width // thumb.width)} × {int(thumb.height * (320 / thumb.width))} px (preview)<br>
        Format: {uploaded_img.type}
    </div>
</div>
""", unsafe_allow_html=True)
            except Exception:
                st.markdown(
                    f'<div style="background:#1E293B;border:1px solid #334155;border-radius:8px;'
                    f'padding:0.6rem 1rem;">🖼️ <strong style="color:#E2E8F0;">{uploaded_img.name}</strong>'
                    f'<span style="color:#94A3B8;margin-left:0.75rem;">{file_size_kb} KB</span></div>',
                    unsafe_allow_html=True,
                )

            if st.button("🔍 Extract Text from Image (OCR)", use_container_width=True, key="extract_img_btn"):
                with st.spinner("Running OCR on resume image…"):
                    img_bytes = uploaded_img.getvalue()
                    extracted, warn = _extract_image_text(img_bytes, uploaded_img.name)

                if warn:
                    if len(extracted) < 20:
                        st.warning(warn)
                    else:
                        st.info(f"ℹ️ {warn}")

                if extracted and len(extracted) >= 20:
                    st.session_state["resume_extracted_text"] = extracted
                    st.success(
                        f"✅ OCR extracted {len(extracted.split())} words. "
                        "Review and edit the text below before analysing."
                    )

    # ══════════════════════════════════════════════════════════════════════════
    # C) Paste Text (always shown — also shows extracted text from A/B)
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("---")
    if input_method == "📋 Paste Resume Text":
        st.markdown("""
<div style="background:rgba(79,70,229,0.08);border:1px solid rgba(79,70,229,0.25);
            border-radius:10px;padding:0.75rem 1rem;margin-bottom:0.5rem;font-size:0.82rem;color:#94A3B8;">
    💡 <strong style="color:#E2E8F0;">Tip:</strong>
    Open your resume in Word or Google Docs → Select All (Ctrl+A) → Copy (Ctrl+C) → Paste below.
    Include all sections: Contact, Summary, Education, Skills, Experience, Projects, Certifications.
</div>
""", unsafe_allow_html=True)
        section_label = "### 📝 Resume Text"
    else:
        section_label = "### 📝 Review & Edit Extracted Resume Text"

    st.markdown(section_label)

    # Determine initial value for text area
    textarea_value = (
        st.session_state.get("resume_extracted_text", "")
        if input_method != "📋 Paste Resume Text"
        else st.session_state.get("resume_input", "")
    )

    resume_text = st.text_area(
        label="Resume text area",
        value=textarea_value,
        height=340,
        placeholder="""John Doe | john@email.com | LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

EDUCATION
B.Tech Computer Science | XYZ University | 2020–2024 | CGPA: 8.5/10

SKILLS
Python, Machine Learning, SQL, TensorFlow, Git, Docker

EXPERIENCE
Data Science Intern | ABC Corp | June 2023 – Aug 2023
• Built a customer churn prediction model with 87% accuracy using Random Forest
• Reduced data processing time by 40% through pipeline optimisation

PROJECTS
Sales Forecasting Dashboard | Python, Prophet, Streamlit
• Developed an interactive dashboard forecasting monthly sales with MAPE < 8%

CERTIFICATIONS
• IBM Data Science Professional Certificate (Coursera, 2023)""",
        key="resume_input",
        label_visibility="collapsed",
    )

    # Action buttons
    btn_col1, btn_col2, btn_col3 = st.columns([3, 1, 1])
    with btn_col1:
        analyse_btn = st.button(
            "🚀 Analyse Resume with IBM watsonx.ai",
            use_container_width=True,
            type="primary",
            key="analyse_resume_btn",
        )
    with btn_col2:
        if st.button("📋 Use Extracted", use_container_width=True,
                     key="use_extracted_btn",
                     disabled=not st.session_state.get("resume_extracted_text", "")):
            st.session_state["resume_input"] = st.session_state.get("resume_extracted_text", "")
            st.rerun()
    with btn_col3:
        if st.button("🗑️ Clear", use_container_width=True, key="clear_resume_btn"):
            st.session_state["resume_input"]          = ""
            st.session_state["resume_extracted_text"] = ""
            st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # Analysis
    # ══════════════════════════════════════════════════════════════════════════
    if analyse_btn:
        if not resume_text or len(resume_text.strip()) < 50:
            st.error(
                "⚠️ Resume text is too short (minimum 50 characters). "
                "Please upload a resume file or paste your resume text above."
            )
        else:
            with st.spinner("🧠 Analysing your resume with IBM watsonx.ai…"):
                model = _get_model()
                if model is None:
                    analysis = _demo_resume_analysis(resume_text)
                else:
                    try:
                        if target_role and target_domain:
                            prompt = _build_resume_prompt(resume_text, target_role, target_domain)
                        else:
                            prompt = _build_generic_resume_prompt(resume_text)
                        result   = model.generate_text(prompt=prompt)
                        analysis = result.strip() if result else _demo_resume_analysis(resume_text)
                    except Exception as e:
                        st.error(f"⚠️ IBM watsonx.ai error: {e}")
                        analysis = _demo_resume_analysis(resume_text)

            st.markdown("---")
            st.markdown("### 📊 Resume Analysis Report")
            if target_role or target_domain:
                role_str   = target_role   or "—"
                domain_str = target_domain or "—"
                st.markdown(
                    f'<div style="background:rgba(79,70,229,0.08);border:1px solid rgba(79,70,229,0.25);'
                    f'border-radius:8px;padding:0.5rem 1rem;margin-bottom:0.75rem;font-size:0.8rem;color:#94A3B8;">'
                    f'Analysed for: <strong style="color:#E2E8F0;">{role_str}</strong> · '
                    f'<strong style="color:#E2E8F0;">{domain_str}</strong></div>',
                    unsafe_allow_html=True,
                )
            st.markdown(
                f'<div style="background:linear-gradient(145deg,#1E293B,#0F172A);'
                f'border:1px solid rgba(79,70,229,0.4);border-radius:14px;'
                f'padding:1.4rem;border-left:4px solid #4F46E5;">{analysis}</div>',
                unsafe_allow_html=True,
            )

            st.markdown("---")
            st.markdown("### 📈 Resume Quick Statistics")
            _render_stats(resume_text)

    # ── Resume Tips ───────────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("📚 Resume Writing Best Practices"):
        tips_col1, tips_col2 = st.columns(2)
        with tips_col1:
            st.markdown("""
**✅ Structure Checklist:**
- [ ] Professional summary / objective (3 lines max)
- [ ] Education (institution, degree, GPA, graduation year)
- [ ] Skills (technical + soft skills, relevant to role)
- [ ] Experience / Internships (reverse chronological)
- [ ] Projects (with tech stack and impact)
- [ ] Certifications & Courses
- [ ] Contact info (email, phone, LinkedIn, GitHub)

**🔤 Language & Tone:**
- Use active voice and strong action verbs
- Start bullets with: Led, Built, Designed, Optimised, Developed
- Quantify: use numbers (%, ₹, K, M, #) wherever possible
""")
        with tips_col2:
            st.markdown("""
**🤖 ATS Optimisation Tips:**
- Mirror exact keywords from the job description
- Avoid tables, columns, or graphics (ATS can't parse them)
- Use standard section headers (Experience, Education, Skills)
- Save/submit as PDF for consistent formatting

**📐 Formatting Rules:**
- Length: 1 page (fresher) · 2 pages (3+ years experience)
- Font: Calibri, Arial, or Times New Roman (11–12pt)
- Margins: 0.75"–1" on all sides
- File name: `FirstName_LastName_Resume.pdf`

**🇮🇳 Indian Job Market Tips:**
- Mention CGPA/percentage (Indian recruiters expect it)
- Include JEE rank / GATE score if strong
- Add relevant hackathon wins or open-source contributions
""")

    # ── OCR installation guide ─────────────────────────────────────────────────
    with st.expander("🔧 Image OCR — Installation Guide"):
        st.markdown("""
**Current OCR Status:**
""")
        # Dynamic status check
        try:
            import pytesseract  # type: ignore
            import shutil
            tess_path = shutil.which("tesseract")
            if tess_path:
                st.success(f"✅ Tesseract OCR is installed and ready: `{tess_path}`")
            else:
                st.warning("⚠️ `pytesseract` Python package is installed but the Tesseract binary is not found in PATH.")
        except ImportError:
            st.warning("⚠️ `pytesseract` is not installed. PDF upload and text paste still work without it.")

        st.markdown("""
**To enable Image OCR (Windows):**
1. Download Tesseract installer: [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer — choose **"Add to system PATH"** during setup
3. Run: `pip install pytesseract`
4. Restart the application

**To enable Image OCR (Linux/macOS):**
```bash
# Ubuntu / Debian
sudo apt install tesseract-ocr
pip install pytesseract

# macOS
brew install tesseract
pip install pytesseract
```

*PDF upload and text paste work without Tesseract — only image-based resume extraction requires it.*
""")
