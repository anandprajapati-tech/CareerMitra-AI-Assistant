# modules/student_profile.py
# CareerMitra AI – Student Profile Management

import streamlit as st
from config.settings import (
    EDUCATION_LEVELS, STREAMS, SKILL_CATEGORIES,
    PROFICIENCY_LEVELS, INTERESTS, COLORS
)
from database.db_manager import (
    save_student, get_student_by_email, get_student_by_id,
    save_skills, get_skills, save_interests, get_interests,
    get_career_goal
)


def render_student_profile(student_id: int | None) -> int | None:
    """
    Render the Student Profile page.
    Returns the student_id after a successful save (or the existing one).
    """
    st.markdown("## 👤 Student Profile")
    st.markdown("Fill in your details to get personalised career guidance.")

    # ── Load existing data if logged in ───────────────────────────────────────
    existing_student = get_student_by_id(student_id) if student_id else None
    existing_skills = get_skills(student_id) if student_id else []
    existing_interests = get_interests(student_id) if student_id else []

    # Convert saved skills to a {name: proficiency} dict for pre-population
    saved_skill_map = {s["skill_name"]: s.get("proficiency", "Beginner") for s in existing_skills}

    tabs = st.tabs(["📋 Basic Info", "🛠️ Skills", "💡 Interests & Goals"])

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 1 – Basic Information
    # ──────────────────────────────────────────────────────────────────────────
    with tabs[0]:
        with st.form("basic_info_form"):
            st.markdown("### Personal Details")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name *", value=existing_student.get("name", "") if existing_student else "")
                email = st.text_input("Email Address *", value=existing_student.get("email", "") if existing_student else "")
                phone = st.text_input("Phone Number", value=existing_student.get("phone", "") if existing_student else "")
            with col2:
                age = st.number_input("Age", min_value=14, max_value=60, value=int(existing_student.get("age") or 18) if existing_student else 18)
                city = st.text_input("City / Location", value=existing_student.get("city", "") if existing_student else "")
                gpa = st.number_input("GPA / Percentage (%)", min_value=0.0, max_value=100.0, step=0.1,
                                      value=float(existing_student.get("gpa") or 0.0) if existing_student else 0.0)

            st.markdown("### Educational Background")
            col3, col4 = st.columns(2)
            with col3:
                education = st.selectbox(
                    "Highest Education Level *",
                    EDUCATION_LEVELS,
                    index=EDUCATION_LEVELS.index(existing_student["education"]) if existing_student and existing_student.get("education") in EDUCATION_LEVELS else 0,
                )
                stream = st.selectbox(
                    "Stream / Branch *",
                    STREAMS,
                    index=STREAMS.index(existing_student["stream"]) if existing_student and existing_student.get("stream") in STREAMS else 0,
                )
            with col4:
                institution = st.text_input(
                    "College / School Name",
                    value=existing_student.get("institution", "") if existing_student else ""
                )

            submitted = st.form_submit_button("💾 Save Basic Info", use_container_width=True)
            if submitted:
                if not name or not email:
                    st.error("Name and Email are required.")
                else:
                    profile = {
                        "name": name, "email": email, "phone": phone,
                        "age": age, "city": city, "education": education,
                        "stream": stream, "institution": institution, "gpa": gpa,
                    }
                    new_id = save_student(profile)
                    st.session_state["student_id"] = new_id
                    st.success(f"✅ Profile saved! Welcome, {name}.")
                    st.rerun()

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 2 – Skills
    # ──────────────────────────────────────────────────────────────────────────
    with tabs[1]:
        if not student_id:
            st.warning("Please save Basic Info first.")
        else:
            st.markdown("### 🛠️ Your Skills")
            st.caption("Select skills you possess and your proficiency level.")

            collected_skills = []
            with st.form("skills_form"):
                for category, skill_list in SKILL_CATEGORIES.items():
                    st.markdown(f"**{category}**")
                    cols = st.columns(2)
                    for i, skill in enumerate(skill_list):
                        with cols[i % 2]:
                            has_skill = skill in saved_skill_map
                            checked = st.checkbox(skill, value=has_skill, key=f"skill_check_{category}_{skill}")
                            if checked:
                                prof = st.selectbox(
                                    f"Level for {skill}",
                                    PROFICIENCY_LEVELS,
                                    index=PROFICIENCY_LEVELS.index(saved_skill_map.get(skill, "Beginner")),
                                    key=f"skill_prof_{category}_{skill}",
                                )
                                collected_skills.append({"name": skill, "category": category, "proficiency": prof})
                    st.markdown("---")

                save_skills_btn = st.form_submit_button("💾 Save Skills", use_container_width=True)
                if save_skills_btn:
                    save_skills(student_id, collected_skills)
                    st.success(f"✅ {len(collected_skills)} skills saved!")
                    st.rerun()

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 3 – Interests & Goals
    # ──────────────────────────────────────────────────────────────────────────
    with tabs[2]:
        if not student_id:
            st.warning("Please save Basic Info first.")
        else:
            st.markdown("### 💡 Your Interests")
            with st.form("interests_form"):
                st.caption("Select all areas that genuinely interest you.")
                selected_interests = []
                cols = st.columns(3)
                for i, interest in enumerate(INTERESTS):
                    with cols[i % 3]:
                        if st.checkbox(interest, value=interest in existing_interests, key=f"interest_{i}"):
                            selected_interests.append(interest)

                save_int_btn = st.form_submit_button("💾 Save Interests", use_container_width=True)
                if save_int_btn:
                    save_interests(student_id, selected_interests)
                    st.success(f"✅ {len(selected_interests)} interests saved!")
                    st.rerun()

    # ── Profile completion hint ───────────────────────────────────────────────
    if student_id:
        _render_completion_checklist(student_id)

    return st.session_state.get("student_id")


def _render_completion_checklist(student_id: int):
    student = get_student_by_id(student_id)
    skills = get_skills(student_id)
    interests = get_interests(student_id)
    goal = get_career_goal(student_id)

    checks = {
        "Basic Info saved": bool(student and student.get("name") and student.get("email")),
        "Education set": bool(student and student.get("education")),
        "Skills added (min 3)": len(skills) >= 3,
        "Interests selected (min 2)": len(interests) >= 2,
        "Career goal set": goal is not None,
    }
    pct = round(sum(checks.values()) / len(checks) * 100)

    st.markdown("---")
    st.markdown("### 📊 Profile Completion")
    progress_color = COLORS["success"] if pct >= 80 else (COLORS["warning"] if pct >= 50 else COLORS["danger"])
    st.markdown(f"""
<div style="background:#1E293B; border:1px solid #334155; border-radius:10px; padding:1rem;">
    <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
        <span style="color:#F1F5F9; font-weight:600;">Completion: {pct}%</span>
    </div>
    <div style="background:#0F172A; border-radius:6px; height:10px; margin-bottom:0.75rem;">
        <div style="background:{progress_color}; height:10px; border-radius:6px; width:{pct}%;"></div>
    </div>
    {"".join(f'<div style="color:{"#10B981" if v else "#94A3B8"}; font-size:0.85rem; padding:2px 0;">{"✅" if v else "⬜"} {k}</div>' for k, v in checks.items())}
</div>
""", unsafe_allow_html=True)
