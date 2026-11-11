# src/pages/interview_prep.py
# CareerMitra AI Assistant – AI Interview Preparation Page (IBM Granite powered)

import streamlit as st
from src.config import COLORS, CAREER_DOMAINS, ibm_configured
from src.database import get_student_by_id, get_career_goal, get_skills
from src.ibm_granite import _get_model, get_model_error

# ── Question Banks (domain-specific) ─────────────────────────────────────────

QUESTION_BANKS = {
    "Technology & Engineering": {
        "Technical": [
            "Explain the difference between process and thread.",
            "What is time complexity? Explain Big-O notation with examples.",
            "Describe how a hash map works internally.",
            "Explain REST API principles and HTTP methods.",
            "What is the difference between SQL and NoSQL databases?",
            "How does a load balancer work? When would you use one?",
            "Explain SOLID principles in software engineering.",
            "What is the difference between TCP and UDP?",
        ],
        "Behavioural": [
            "Tell me about a time you debugged a complex issue under pressure.",
            "Describe a project you're most proud of and your contribution.",
            "How do you prioritise tasks when working on multiple features?",
            "Tell me about a time you received critical feedback and how you handled it.",
        ],
        "HR": [
            "Why do you want to work in software engineering?",
            "Where do you see yourself in 5 years?",
            "What is your greatest technical strength?",
            "Describe your ideal work environment.",
        ],
    },
    "Data Science & AI/ML": {
        "Technical": [
            "Explain the bias-variance tradeoff in machine learning.",
            "What is overfitting? How do you prevent it?",
            "Explain the difference between supervised and unsupervised learning.",
            "What is cross-validation and why is it important?",
            "Describe how gradient descent works.",
            "What metrics would you use to evaluate a classification model?",
            "Explain transformer architecture in NLP.",
            "How do you handle missing data in a dataset?",
        ],
        "Behavioural": [
            "Walk me through a data science project from problem to deployment.",
            "Describe a time your model failed in production and how you fixed it.",
            "How do you explain ML concepts to non-technical stakeholders?",
            "Tell me about a time you found surprising insights in data.",
        ],
        "HR": [
            "Why are you passionate about data science?",
            "How do you stay updated with the latest AI/ML research?",
            "Describe a time you collaborated with a cross-functional team.",
            "What is your approach to learning a new ML framework?",
        ],
    },
    "Business & Management": {
        "Technical": [
            "Walk me through how you'd perform a market sizing exercise.",
            "What is the difference between revenue and profit? Explain EBITDA.",
            "How do you build a financial model in Excel?",
            "Explain Porter's Five Forces with an example.",
            "How would you conduct a SWOT analysis for a new product?",
            "What is Net Promoter Score (NPS) and how is it used?",
            "Explain the BCG matrix and how you'd use it.",
            "How do you measure the ROI of a business initiative?",
        ],
        "Behavioural": [
            "Describe a time you led a team through a difficult project.",
            "Tell me about a situation where you had to influence without authority.",
            "How did you handle a conflict within your team?",
            "Describe a time you made a data-driven decision.",
        ],
        "HR": [
            "Why consulting / management / product management?",
            "What's your leadership style?",
            "Where do you see yourself in 5 years?",
            "Tell me about yourself in 2 minutes.",
        ],
    },
    "Finance & Accounting": {
        "Technical": [
            "Walk me through a DCF (Discounted Cash Flow) analysis.",
            "What is working capital and why does it matter?",
            "Explain the three financial statements and how they connect.",
            "What is the difference between a balance sheet and income statement?",
            "How do you value a company using comparable analysis?",
            "What is WACC and how is it calculated?",
            "Explain the difference between equity and debt financing.",
            "What is goodwill in accounting?",
        ],
        "Behavioural": [
            "Describe a time you identified a financial error and corrected it.",
            "How do you handle tight deadlines during month-end closing?",
            "Tell me about a time you presented complex financial data to management.",
        ],
        "HR": [
            "Why finance / accounting / investment banking?",
            "What drew you to the CA / CFA / finance track?",
            "Describe your attention to detail with an example.",
            "How do you stay updated with regulatory changes?",
        ],
    },
}

DEFAULT_QUESTIONS = {
    "Technical": [
        "Describe a technical challenge you've faced and how you solved it.",
        "What tools and technologies are you most proficient in?",
        "How do you approach learning a new technical skill?",
        "Describe the most complex project you've worked on.",
    ],
    "Behavioural": [
        "Tell me about yourself (2–3 minutes).",
        "Describe a time you showed leadership.",
        "Tell me about a failure and what you learned.",
        "How do you handle stress and tight deadlines?",
    ],
    "HR": [
        "Why do you want to join this company?",
        "What are your salary expectations?",
        "Where do you see yourself in 5 years?",
        "What is your biggest strength and weakness?",
    ],
}


def _build_interview_prompt(question: str, domain: str, student_name: str, skills: list[str]) -> str:
    return f"""You are an expert interview coach helping {student_name} prepare for interviews in {domain}.

Question: {question}

Student's skills: {', '.join(skills[:10]) if skills else 'General'}

Please provide:
1. **Model Answer** — A well-structured, impressive answer using the STAR method where relevant (2–3 paragraphs)
2. **Key Points to Include** — 3–4 bullet points of critical elements the answer must contain
3. **Common Mistakes** — 2 mistakes candidates often make answering this question
4. **Expert Tip** — One insider tip to stand out from other candidates

Keep the model answer natural, confident, and approximately 150–200 words.
Response:"""


def _demo_answer(question: str, domain: str) -> str:
    return f"""**📝 Model Answer for: "{question[:80]}..."**

**Example Answer (STAR Format):**

"In my experience at [Company/Project], I encountered a similar challenge where I needed to [situation]. 
My task was to [task/responsibility].

I approached this by first [action step 1], then [action step 2], and finally [action step 3]. 
I collaborated with [team/stakeholders] and used my skills in [relevant skill] to ensure the outcome met expectations.

As a result, we achieved [specific measurable outcome]. This experience taught me [key learning], 
which I apply in every project I take on today."

**🎯 Key Points to Include:**
• Use the STAR method: Situation → Task → Action → Result
• Quantify your results whenever possible (%, numbers, timeframes)
• Highlight relevant technical and soft skills for {domain}
• Show self-awareness and growth mindset

**⚠️ Common Mistakes:**
• Being too vague — always use a specific real example
• Forgetting the "Result" — always close with the impact you made

**💡 Expert Tip:**
Prepare 5–6 strong STAR stories in advance that can be adapted to different questions. Practice out loud until they feel natural.

*Connect IBM watsonx.ai for a fully personalised AI answer.*"""


def render_interview_prep(student_id: int | None):
    st.markdown("## 🎤 AI Interview Preparation")
    st.markdown("Practice domain-specific interview questions with AI-generated model answers and expert coaching tips.")

    # Status
    ibm_ok = ibm_configured()
    model_error = get_model_error()
    status_color = "#10B981" if ibm_ok and not model_error else ("#EF4444" if model_error else "#F59E0B")
    status_text  = "IBM Granite Connected" if ibm_ok and not model_error else \
                   ("Configuration Error" if model_error else "Demo Mode")
    st.markdown(f"""
<div style="display:inline-flex;align-items:center;gap:0.5rem;background:#1E293B;
            border:1px solid #334155;border-radius:20px;padding:0.3rem 0.85rem;
            margin-bottom:0.8rem;font-size:0.8rem;">
    <span style="width:8px;height:8px;border-radius:50%;background:{status_color};display:inline-block;"></span>
    <span style="color:{status_color};">{status_text}</span>
</div>
""", unsafe_allow_html=True)

    if model_error and ibm_ok:
        with st.expander("⚠️ IBM Granite Configuration Error", expanded=True):
            st.markdown(model_error)

    student = get_student_by_id(student_id) if student_id else None
    goal    = get_career_goal(student_id) if student_id else None
    skills  = get_skills(student_id) if student_id else []
    student_name = student.get("name", "Student") if student else "Student"
    skill_names  = [s["skill_name"] for s in skills]

    # ── Domain & Type Selection ───────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        available_domains = list(QUESTION_BANKS.keys())
        if goal and goal.get("goal_domain") in available_domains:
            default_idx = available_domains.index(goal["goal_domain"])
        else:
            default_idx = 0
        domain = st.selectbox("🎯 Interview Domain:", available_domains, index=default_idx)
    with col2:
        q_type = st.selectbox("📂 Question Type:", ["Technical", "Behavioural", "HR"])
    with col3:
        mode = st.selectbox("🔧 Mode:", ["Practice Questions", "Custom Question", "Mock Interview"])

    st.markdown("---")

    questions = QUESTION_BANKS.get(domain, DEFAULT_QUESTIONS).get(q_type, [])

    if mode == "Practice Questions":
        _practice_mode(questions, domain, student_name, skill_names, q_type)

    elif mode == "Custom Question":
        _custom_mode(domain, student_name, skill_names)

    elif mode == "Mock Interview":
        _mock_interview_mode(domain, student_name, skill_names, questions)


def _practice_mode(questions: list[str], domain: str, student_name: str, skills: list[str], q_type: str):
    st.markdown(f"### 📋 {q_type} Questions — {domain}")
    st.markdown(f"*{len(questions)} questions available. Click any to get an AI-generated model answer.*")

    # Display all questions as cards
    for i, question in enumerate(questions, 1):
        with st.expander(f"**Q{i}.** {question}"):
            if st.button(f"🤖 Get AI Model Answer for Q{i}", key=f"ans_{i}", use_container_width=True):
                with st.spinner("IBM Granite is generating a model answer..."):
                    model = _get_model()
                    if model is None:
                        answer = _demo_answer(question, domain)
                    else:
                        try:
                            prompt = _build_interview_prompt(question, domain, student_name, skills)
                            result = model.generate_text(prompt=prompt)
                            answer = result.strip() if result else _demo_answer(question, domain)
                        except Exception as e:
                            answer = f"⚠️ Error: {e}\n\n{_demo_answer(question, domain)}"
                st.markdown(f"""
<div style="background:#0A0F1E;border:1px solid rgba(79,70,229,0.35);border-radius:10px;
            padding:1.1rem;border-left:3px solid #4F46E5;margin-top:0.5rem;">
{answer}
</div>
""", unsafe_allow_html=True)

    # Interview tips
    st.markdown("---")
    _interview_tips()


def _custom_mode(domain: str, student_name: str, skills: list[str]):
    st.markdown(f"### 💬 Custom Question — {domain}")
    st.markdown("Enter any interview question to get a personalised AI model answer.")

    custom_q = st.text_area(
        "Your Interview Question:",
        height=100,
        placeholder="e.g., How would you design a scalable system for 1 million concurrent users?",
        key="custom_q",
    )

    if st.button("🤖 Get AI Model Answer", use_container_width=True, disabled=not custom_q.strip()):
        if custom_q.strip():
            with st.spinner("IBM Granite is generating a model answer..."):
                model = _get_model()
                if model is None:
                    answer = _demo_answer(custom_q, domain)
                else:
                    try:
                        prompt = _build_interview_prompt(custom_q, domain, student_name, skills)
                        result = model.generate_text(prompt=prompt)
                        answer = result.strip() if result else _demo_answer(custom_q, domain)
                    except Exception as e:
                        answer = f"⚠️ Error: {e}\n\n{_demo_answer(custom_q, domain)}"
            st.markdown("---")
            st.markdown("### 💡 Model Answer")
            st.markdown(f"""
<div style="background:linear-gradient(145deg,#1E293B,#0F172A);border:1px solid rgba(79,70,229,0.4);
            border-radius:14px;padding:1.4rem;border-left:4px solid #4F46E5;">
{answer}
</div>
""", unsafe_allow_html=True)


def _mock_interview_mode(domain: str, student_name: str, skills: list[str], questions: list[str]):
    st.markdown(f"### 🎬 Mock Interview — {domain}")
    st.markdown("Simulate a real interview. Answer each question, then get AI feedback on your response.")

    if "mock_q_idx" not in st.session_state:
        st.session_state["mock_q_idx"] = 0
        st.session_state["mock_answers"] = []

    q_idx = st.session_state["mock_q_idx"]
    total = min(len(questions), 5)  # 5 questions per mock session

    if q_idx >= total:
        st.success(f"🎉 Mock interview complete! You answered {total} questions.")
        if st.button("🔄 Restart Mock Interview", use_container_width=True):
            st.session_state["mock_q_idx"] = 0
            st.session_state["mock_answers"] = []
            st.rerun()
        return

    # Progress
    st.markdown(f"""
<div style="background:#1E293B;border-radius:8px;height:8px;margin-bottom:1rem;">
    <div style="background:linear-gradient(90deg,#4F46E5,#06B6D4);height:8px;border-radius:8px;
                width:{int((q_idx/total)*100)}%;"></div>
</div>
<div style="color:#94A3B8;font-size:0.78rem;margin-bottom:1rem;">Question {q_idx+1} of {total}</div>
""", unsafe_allow_html=True)

    current_q = questions[q_idx]
    st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(79,70,229,0.12),rgba(6,182,212,0.06));
            border:1px solid rgba(79,70,229,0.3);border-radius:12px;padding:1.2rem;margin-bottom:1rem;">
    <div style="color:#94A3B8;font-size:0.75rem;font-weight:600;margin-bottom:0.4rem;">QUESTION {q_idx+1}</div>
    <div style="color:#E2E8F0;font-size:1.05rem;font-weight:600;">{current_q}</div>
</div>
""", unsafe_allow_html=True)

    user_answer = st.text_area(
        "Your Answer:",
        height=140,
        placeholder="Type your answer here as if you're speaking in a real interview...",
        key=f"mock_ans_{q_idx}",
    )

    col_submit, col_skip = st.columns(2)
    with col_submit:
        if st.button("✅ Submit & Get Feedback", use_container_width=True, disabled=not user_answer.strip()):
            if user_answer.strip():
                with st.spinner("IBM Granite is evaluating your answer..."):
                    model = _get_model()
                    feedback_prompt = f"""You are an interview coach. Evaluate this candidate's answer.

Question: {current_q}
Domain: {domain}
Candidate's Answer: {user_answer}

Provide:
1. **Score** (out of 10) with a one-line justification
2. **What you did well** (1–2 specific points)
3. **How to improve** (1–2 specific, actionable points)  
4. **Model Answer** (a better version in 3–4 sentences)

Be encouraging but honest.
Feedback:"""
                    if model is None:
                        feedback = f"""**Score: 7/10** — Good effort with relevant content.

**What you did well:** You addressed the core question and showed understanding of the domain.

**How to improve:** Use the STAR method more explicitly (Situation, Task, Action, Result) and quantify your achievements.

**Model Answer:** "{current_q[:50]}..." — When answering this, start with a specific example from your experience, describe your actions clearly, and conclude with a measurable result. This demonstrates both competence and impact.

*Connect IBM watsonx.ai for detailed personalised feedback.*"""
                    else:
                        try:
                            result = model.generate_text(prompt=feedback_prompt)
                            feedback = result.strip() if result else "Unable to generate feedback. Please try again."
                        except Exception as e:
                            feedback = f"⚠️ Error: {e}"

                st.markdown(f"""
<div style="background:#1E293B;border:1px solid rgba(16,185,129,0.3);border-radius:10px;
            padding:1.1rem;border-left:3px solid #10B981;margin:0.75rem 0;">
{feedback}
</div>
""", unsafe_allow_html=True)
                st.session_state["mock_answers"].append({"question": current_q, "answer": user_answer})
                if st.button("→ Next Question", use_container_width=True):
                    st.session_state["mock_q_idx"] = q_idx + 1
                    st.rerun()
    with col_skip:
        if st.button("⏭ Skip Question", use_container_width=True):
            st.session_state["mock_q_idx"] = q_idx + 1
            st.rerun()


def _interview_tips():
    with st.expander("💡 Interview Success Tips"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
**🎯 Before the Interview:**
- Research the company thoroughly (products, culture, recent news)
- Prepare 5–6 STAR stories covering different competencies
- Practice answering out loud (not just in your head)
- Prepare 3 thoughtful questions to ask the interviewer
- Dress professionally and arrive/join 5 minutes early

**📣 During the Interview:**
- Listen carefully — ask for clarification if needed
- Use the STAR method for behavioural questions
- Think out loud for technical/case questions
- Be specific — use real examples, not hypothetical ones
- Pause and think before answering complex questions
""")
        with col2:
            st.markdown("""
**🇮🇳 India-Specific Tips:**
- For IIT/NIT/top college interviews: expect DSA + system design
- For service companies (TCS, Infosys): focus on aptitude + communication
- For startups: show initiative, product thinking, and adaptability
- For GATE-based PSUs: study core subjects deeply
- For MBA interviews: prepare GD topics and case studies

**💬 Common Questions to Always Prepare:**
- "Tell me about yourself" (2-minute pitch)
- "Why this company/role?"
- "Your greatest achievement"
- "A challenge you overcame"
- "Where do you see yourself in 5 years?"
""")
