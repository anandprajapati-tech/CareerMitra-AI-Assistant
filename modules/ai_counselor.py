# modules/ai_counselor.py
# CareerMitra AI – AI Career Counselor Agent (GPT-powered)

import streamlit as st
from openai import OpenAI
from config.settings import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS
from database.db_manager import (
    save_chat_message, get_chat_history, clear_chat_history,
    get_student_by_id, get_skills, get_interests, get_career_goal
)


def _build_system_prompt(student_id: int) -> str:
    """Construct a personalised system prompt from the student's stored profile."""
    student = get_student_by_id(student_id) if student_id else None
    skills = get_skills(student_id) if student_id else []
    interests = get_interests(student_id) if student_id else []
    goal = get_career_goal(student_id) if student_id else None

    profile_context = ""
    if student:
        skill_names = ", ".join([s["skill_name"] for s in skills]) or "Not specified"
        interest_names = ", ".join(interests) or "Not specified"
        profile_context = f"""
You have the following information about the student:
- Name: {student.get('name', 'N/A')}
- Education: {student.get('education', 'N/A')} in {student.get('stream', 'N/A')}
- Institution: {student.get('institution', 'N/A')}
- Location: {student.get('city', 'N/A')}
- Skills: {skill_names}
- Interests: {interest_names}
- Career Goal: {goal.get('goal_domain', 'N/A') if goal else 'Not set'} → {goal.get('target_role', 'N/A') if goal else 'Not set'}
"""

    return f"""You are CareerMitra, a highly experienced and empathetic AI career counselor specialising in the Indian job market and global career opportunities for students.

Your role is to:
1. Provide personalised, actionable career guidance
2. Help students discover suitable career paths based on their strengths and interests
3. Advise on skill development, certifications, and educational pathways
4. Share insights about job market trends, salary expectations, and growth opportunities
5. Motivate and support students through career decision-making challenges
6. Recommend specific resources: courses, books, communities, and mentors

Guidelines:
- Always be encouraging, professional, and student-centric
- Use simple language; avoid unnecessary jargon
- Back advice with real examples and data where possible
- For Indian students, reference relevant exams (UPSC, CAT, GATE, GRE, etc.) and institutions (IITs, IIMs, AIIMS, NID, etc.)
- If a student seems confused or overwhelmed, break advice into small, manageable steps

{profile_context}

Always end responses with a clear next step or question to keep the conversation productive."""


def render_ai_counselor(student_id: int | None):
    """Render the AI Career Counselor chat interface."""

    st.markdown("## 🤖 AI Career Counselor")
    st.markdown("Chat with your personal AI career advisor. Ask anything about careers, skills, studies, or your future!")

    # ── API key check ─────────────────────────────────────────────────────────
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        st.warning("⚠️ OpenAI API key not configured. Please add your key to the `.env` file to enable AI responses.")
        st.info("**Demo mode:** You can still browse other modules. Add `OPENAI_API_KEY=sk-...` to a `.env` file in the project root to activate the AI counselor.")
        _render_demo_chat()
        return

    if not student_id:
        st.info("👤 Please complete your **Student Profile** first to get personalised career advice.")

    # ── Initialise session state ───────────────────────────────────────────────
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
        if student_id:
            history = get_chat_history(student_id)
            st.session_state.chat_messages = [{"role": h["role"], "content": h["message"]} for h in history]

    # ── Controls row ──────────────────────────────────────────────────────────
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            if student_id:
                clear_chat_history(student_id)
            st.rerun()

    # ── Render chat history ───────────────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_messages:
            st.markdown("""
<div style="text-align:center; padding: 2rem; color: #94A3B8;">
    <div style="font-size: 3rem;">🎓</div>
    <p style="font-size: 1.1rem; font-weight: 600;">Welcome to CareerMitra!</p>
    <p>Start a conversation — ask me about career options, skill development, or study paths.</p>
    <p style="font-size: 0.85rem; opacity: 0.7;">Try: <em>"What career suits a PCB student who likes technology?"</em></p>
</div>
""", unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

    # ── Suggested questions ───────────────────────────────────────────────────
    if not st.session_state.chat_messages:
        st.markdown("**💡 Quick start questions:**")
        suggestions = [
            "What are the best career options for a PCM student in India?",
            "How do I transition from engineering to data science?",
            "What skills should I learn to become an AI/ML engineer?",
            "Compare MBA vs. MS abroad — which is better for my career?",
        ]
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            if cols[i % 2].button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                _process_message(suggestion, student_id)
                st.rerun()

    # ── Chat input ────────────────────────────────────────────────────────────
    if user_input := st.chat_input("Ask your career question here..."):
        _process_message(user_input, student_id)
        st.rerun()


def _process_message(user_input: str, student_id: int | None):
    """Send user message to GPT and store both turns."""
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    if student_id:
        save_chat_message(student_id, "user", user_input)

    client = OpenAI(api_key=OPENAI_API_KEY)
    system_prompt = _build_system_prompt(student_id)

    messages_payload = [{"role": "system", "content": system_prompt}]
    messages_payload += st.session_state.chat_messages[-20:]  # keep last 20 turns for context

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages_payload,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"⚠️ I'm having trouble connecting right now. Error: {str(e)}\n\nPlease check your API key and try again."

    st.session_state.chat_messages.append({"role": "assistant", "content": reply})
    if student_id:
        save_chat_message(student_id, "assistant", reply)


def _render_demo_chat():
    """Show a demo conversation when no API key is available."""
    st.markdown("---")
    st.markdown("**📋 Demo Conversation Preview:**")
    demo_messages = [
        ("user", "I am a 12th standard PCM student. I love coding but also find finance interesting. What career should I consider?"),
        ("assistant", """Great question! With PCM + coding skills + finance interest, you have some powerful combinations:

**🔥 Top Recommendations for You:**

1. **FinTech Engineering** – Build financial products using code (Python, Java). Companies like Zerodha, CRED, and Razorpay are hiring massively.

2. **Quantitative Finance / Algorithmic Trading** – Use mathematics and programming to build trading models. Roles: Quant Developer, Risk Analyst.

3. **Data Science for Finance** – Apply ML to financial data — fraud detection, credit scoring, portfolio optimization.

4. **Computer Science + Finance Minor** – Do B.Tech CS at an IIT/NIT + minor in Economics/Finance for the best of both worlds.

**Immediate Next Steps:**
- Start with Python (it connects coding + finance perfectly)
- Take a free introductory finance course on Coursera
- Explore JEE preparation if targeting IITs

Which of these excites you most? I can dive deeper into any path! 🚀"""),
    ]
    for role, content in demo_messages:
        with st.chat_message(role):
            st.markdown(content)
