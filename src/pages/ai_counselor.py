# src/pages/ai_counselor.py
# CareerMitra AI – AI Counselor Page (IBM Granite)

import streamlit as st
from src.config import ibm_configured, COLORS
from src.database import (
    get_student_by_id, get_skills, get_interests, get_career_goal,
    save_chat_message, get_chat_history, clear_chat_history,
)
from src.ibm_granite import granite_chat, get_model_error


def _build_student_context(student_id: int | None) -> str:
    if not student_id:
        return "Student profile not yet created."
    s = get_student_by_id(student_id)
    if not s:
        return "Student profile not found."
    skills = get_skills(student_id)
    interests = get_interests(student_id)
    goal = get_career_goal(student_id)
    skill_names = ", ".join(sk["skill_name"] for sk in skills) or "Not specified"
    interest_names = ", ".join(interests) or "Not specified"
    return (
        f"Name: {s.get('name','N/A')} | Age: {s.get('age','N/A')} | City: {s.get('city','N/A')}\n"
        f"Education: {s.get('education','N/A')} in {s.get('stream','N/A')}\n"
        f"Institution: {s.get('institution','N/A')} | GPA: {s.get('gpa','N/A')}\n"
        f"Skills: {skill_names}\n"
        f"Interests: {interest_names}\n"
        f"Career Goal: {goal.get('goal_domain','N/A')} → {goal.get('target_role','N/A')}" if goal
        else f"Name: {s.get('name','N/A')} | Education: {s.get('education','N/A')} | Skills: {skill_names}\nInterests: {interest_names}\nCareer Goal: Not set"
    )


def render_ai_counselor(student_id: int | None):
    st.markdown("## 🤖 AI Career Counselor")
    st.markdown("Powered by **IBM Granite** via IBM watsonx.ai — your personalised career advisor.")

    # IBM badge — show connection status and any error
    model_error = get_model_error()
    if not ibm_configured():
        status_color = COLORS["warning"]
        status_text  = "Demo Mode — add IBM credentials to .env"
    elif model_error:
        status_color = COLORS["danger"]
        status_text  = "IBM Granite ⚠️ Configuration Error"
    else:
        status_color = COLORS["success"]
        status_text  = "IBM Granite Connected"

    st.markdown(f"""
<div style="display:inline-flex;align-items:center;gap:0.5rem;background:#1E293B;
            border:1px solid #334155;border-radius:20px;padding:0.3rem 0.8rem;
            margin-bottom:1rem;font-size:0.8rem;">
    <span style="width:8px;height:8px;border-radius:50%;background:{status_color};display:inline-block;"></span>
    <span style="color:{status_color};">{status_text}</span>
</div>
""", unsafe_allow_html=True)

    if model_error and ibm_configured():
        with st.expander("⚠️ IBM Granite Configuration Error — click to see fix", expanded=True):
            st.markdown(model_error)

    if not student_id:
        st.info("👤 Create your **Student Profile** first for personalised advice.")

    # Init session chat
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
        if student_id:
            history = get_chat_history(student_id)
            st.session_state.chat_messages = [{"role": h["role"], "content": h["message"]} for h in history]

    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.chat_messages = []
            if student_id:
                clear_chat_history(student_id)
            st.rerun()

    # Chat display
    if not st.session_state.chat_messages:
        st.markdown("""
<div style="text-align:center;padding:2.5rem;color:#94A3B8;">
    <div style="font-size:3rem;">🎓</div>
    <p style="font-size:1.1rem;font-weight:600;color:#F1F5F9;">Welcome to CareerMitra!</p>
    <p>Ask me anything about careers, skills, or your future path.</p>
    <p style="font-size:0.82rem;opacity:0.7;">Try: <em>"What career suits a PCM student who loves coding?"</em></p>
</div>
""", unsafe_allow_html=True)

        st.markdown("**💡 Quick start:**")
        suggestions = [
            "What career options suit a PCM student in India?",
            "How do I transition from engineering to data science?",
            "What skills should I learn for AI/ML engineering?",
            "Compare MBA vs MS abroad for career growth?",
        ]
        cols = st.columns(2)
        for i, s in enumerate(suggestions):
            if cols[i % 2].button(s, key=f"sug_{i}", use_container_width=True):
                _process_message(s, student_id)
                st.rerun()
    else:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if user_input := st.chat_input("Ask your career question..."):
        _process_message(user_input, student_id)
        st.rerun()


def _process_message(user_input: str, student_id: int | None):
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    if student_id:
        save_chat_message(student_id, "user", user_input)

    context = _build_student_context(student_id)
    history = [{"role": m["role"], "content": m["content"]}
               for m in st.session_state.chat_messages[:-1][-10:]]

    with st.spinner("IBM Granite is thinking..."):
        reply = granite_chat(context, history, user_input)

    st.session_state.chat_messages.append({"role": "assistant", "content": reply})
    if student_id:
        save_chat_message(student_id, "assistant", reply)
