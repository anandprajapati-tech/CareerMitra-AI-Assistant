# src/pages/student_profile.py
# CareerMitra AI Assistant – Student Profile Page

import streamlit as st
from src.config import (
    EDUCATION_LEVELS, STREAMS, SKILL_CATEGORIES, PROFICIENCY_LEVELS,
    INTERESTS, CAREER_DOMAINS, COLORS,
)
from src.database import (
    save_student, get_student_by_id, save_skills, get_skills,
    save_interests, get_interests, get_career_goal, save_career_goal,
)


def render_student_profile(student_id: int | None) -> int | None:
    st.markdown("## 👤 Student Profile")
    st.markdown("Complete your profile to unlock personalised career guidance powered by IBM Granite.")

    existing = get_student_by_id(student_id) if student_id else None
    saved_skills = get_skills(student_id) if student_id else []
    saved_interests = get_interests(student_id) if student_id else []
    skill_map = {s["skill_name"]: s.get("proficiency", "Beginner") for s in saved_skills}

    tab1, tab2, tab3 = st.tabs(["📋 Basic Info", "🛠️ Skills", "💡 Interests & Career Goal"])

    # ── TAB 1 ──────────────────────────────────────────────────────────────────
    with tab1:
        with st.form("basic_info_form"):
            st.markdown("### Personal Details")
            c1, c2 = st.columns(2)
            with c1:
                name  = st.text_input("Full Name *", value=existing.get("name","") if existing else "")
                email = st.text_input("Email Address *", value=existing.get("email","") if existing else "")
                phone = st.text_input("Phone", value=existing.get("phone","") if existing else "")
            with c2:
                age  = st.number_input("Age", min_value=14, max_value=60,
                                       value=int(existing.get("age") or 18) if existing else 18)
                city = st.text_input("City", value=existing.get("city","") if existing else "")
                gpa  = st.number_input("GPA / Percentage (%)", 0.0, 100.0, step=0.1,
                                       value=float(existing.get("gpa") or 0.0) if existing else 0.0)

            st.markdown("### Education")
            c3, c4 = st.columns(2)
            with c3:
                edu = st.selectbox("Education Level *", EDUCATION_LEVELS,
                    index=EDUCATION_LEVELS.index(existing["education"])
                    if existing and existing.get("education") in EDUCATION_LEVELS else 0)
                stream = st.selectbox("Stream / Branch *", STREAMS,
                    index=STREAMS.index(existing["stream"])
                    if existing and existing.get("stream") in STREAMS else 0)
            with c4:
                institution = st.text_input("College / School",
                                            value=existing.get("institution","") if existing else "")

            if st.form_submit_button("💾 Save Basic Info", use_container_width=True):
                if not name or not email:
                    st.error("Name and Email are required.")
                else:
                    new_id = save_student({
                        "name": name, "email": email, "phone": phone, "age": age,
                        "city": city, "education": edu, "stream": stream,
                        "institution": institution, "gpa": gpa,
                    })
                    st.session_state["student_id"] = new_id
                    st.success(f"✅ Profile saved for **{name}**!")
                    st.rerun()

    # ── TAB 2 ──────────────────────────────────────────────────────────────────
    with tab2:
        if not student_id:
            st.info("Save Basic Info first to add skills.")
        else:
            st.markdown("### 🛠️ Your Skills")
            collected = []
            with st.form("skills_form"):
                for cat, skill_list in SKILL_CATEGORIES.items():
                    st.markdown(f"**{cat}**")
                    cols = st.columns(2)
                    for i, skill in enumerate(skill_list):
                        with cols[i % 2]:
                            if st.checkbox(skill, value=skill in skill_map, key=f"chk_{cat}_{skill}"):
                                prof = st.selectbox(f"Level – {skill}", PROFICIENCY_LEVELS,
                                    index=PROFICIENCY_LEVELS.index(skill_map.get(skill,"Beginner")),
                                    key=f"prof_{cat}_{skill}")
                                collected.append({"name": skill, "category": cat, "proficiency": prof})
                    st.markdown("---")
                if st.form_submit_button("💾 Save Skills", use_container_width=True):
                    save_skills(student_id, collected)
                    st.success(f"✅ {len(collected)} skills saved!")
                    st.rerun()

    # ── TAB 3 ──────────────────────────────────────────────────────────────────
    with tab3:
        if not student_id:
            st.info("Save Basic Info first to add interests and career goal.")
        else:
            # ── Interests ─────────────────────────────────────────────────────
            st.markdown("### 💡 Interests")
            sel_interests = []
            with st.form("interests_form"):
                cols = st.columns(3)
                for i, interest in enumerate(INTERESTS):
                    with cols[i % 3]:
                        if st.checkbox(interest, value=interest in saved_interests, key=f"int_{i}"):
                            sel_interests.append(interest)
                if st.form_submit_button("💾 Save Interests", use_container_width=True):
                    save_interests(student_id, sel_interests)
                    st.success(f"✅ {len(sel_interests)} interests saved!")
                    st.rerun()

            # ── Career Goal ───────────────────────────────────────────────────
            st.markdown("---")
            existing_goal = get_career_goal(student_id)

            # Status badge
            if existing_goal and existing_goal.get("target_role"):
                st.markdown("""
<div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.35);
            border-radius:10px;padding:0.6rem 1rem;margin-bottom:0.75rem;
            display:flex;align-items:center;gap:0.6rem;">
    <span style="font-size:1.2rem;">✅</span>
    <span style="color:#10B981;font-weight:600;font-size:0.9rem;">Career Goal saved</span>
</div>
""", unsafe_allow_html=True)

            st.markdown("### 🎯 Career Goal")
            st.markdown(
                "Define your career goal so IBM Granite AI can personalise every recommendation, "
                "skill gap analysis, roadmap, and career path specifically for you."
            )

            # Pre-fill from DB if available
            pre_role     = existing_goal.get("target_role", "")   if existing_goal else ""
            pre_domain   = existing_goal.get("goal_domain", "")   if existing_goal else ""
            pre_notes    = existing_goal.get("notes", "")         if existing_goal else ""
            pre_timeline = existing_goal.get("target_timeline", "") if existing_goal else ""

            # Split stored notes into objective / location / work_mode sub-fields
            # Format stored in notes: "objective|||location|||work_mode"
            notes_parts  = pre_notes.split("|||") if pre_notes else []
            pre_objective  = notes_parts[0] if len(notes_parts) > 0 else ""
            pre_location   = notes_parts[1] if len(notes_parts) > 1 else ""
            pre_work_mode  = notes_parts[2] if len(notes_parts) > 2 else "No Preference"

            work_modes = ["No Preference", "On-site", "Hybrid", "Work from Home"]

            with st.form("career_goal_form"):
                g1, g2 = st.columns(2)
                with g1:
                    target_role = st.text_input(
                        "🏆 Target Career / Dream Job *",
                        value=pre_role,
                        placeholder="e.g., Data Scientist, Software Engineer, Product Manager",
                    )
                with g2:
                    domain_options = ["Select a domain…"] + CAREER_DOMAINS
                    domain_default = (domain_options.index(pre_domain)
                                      if pre_domain in domain_options else 0)
                    goal_domain = st.selectbox(
                        "🏢 Preferred Industry / Domain *",
                        options=domain_options,
                        index=domain_default,
                    )

                career_objective = st.text_area(
                    "📝 Career Objective",
                    value=pre_objective,
                    height=110,
                    placeholder=(
                        "e.g., I want to become a Data Scientist specialising in AI/ML within "
                        "2 years by building strong Python and ML skills, earning IBM certifications, "
                        "and working at a product-based company."
                    ),
                )

                g3, g4, g5 = st.columns(3)
                with g3:
                    timeline_opts = [
                        "Within 6 months", "6–12 months", "1–2 years",
                        "2–3 years", "3–5 years", "5+ years",
                    ]
                    tl_default = (timeline_opts.index(pre_timeline)
                                  if pre_timeline in timeline_opts else 2)
                    target_timeline = st.selectbox(
                        "⏱️ Target Timeline",
                        options=timeline_opts,
                        index=tl_default,
                    )
                with g4:
                    preferred_location = st.text_input(
                        "📍 Preferred Job Location",
                        value=pre_location,
                        placeholder="e.g., Bengaluru, Mumbai, Remote",
                    )
                with g5:
                    wm_default = (work_modes.index(pre_work_mode)
                                  if pre_work_mode in work_modes else 0)
                    work_mode = st.selectbox(
                        "💼 Preferred Work Mode",
                        options=work_modes,
                        index=wm_default,
                    )

                submitted = st.form_submit_button(
                    "🎯 Save Career Goal", use_container_width=True
                )

            if submitted:
                if not target_role.strip():
                    st.error("⚠️ Target Career / Dream Job is required.")
                elif goal_domain == "Select a domain…":
                    st.error("⚠️ Please select a Preferred Industry / Domain.")
                else:
                    # Pack the three sub-fields into the existing `notes` column
                    packed_notes = "|||".join([
                        career_objective.strip(),
                        preferred_location.strip(),
                        work_mode,
                    ])
                    save_career_goal(student_id, {
                        "domain":   goal_domain,
                        "role":     target_role.strip(),
                        "timeline": target_timeline,
                        "notes":    packed_notes,
                    })
                    st.success(
                        f"✅ Career Goal saved! "
                        f"Target: **{target_role.strip()}** in **{goal_domain}**"
                    )
                    st.rerun()

    # ── Completion indicator ───────────────────────────────────────────────────
    if student_id:
        _completion_bar(student_id)

    return st.session_state.get("student_id")


def _completion_bar(student_id: int):
    s = get_student_by_id(student_id)
    skills = get_skills(student_id)
    interests = get_interests(student_id)
    goal = get_career_goal(student_id)
    checks = {
        "Basic Info": bool(s and s.get("name") and s.get("email")),
        "Education":  bool(s and s.get("education")),
        "Skills (3+)": len(skills) >= 3,
        "Interests (2+)": len(interests) >= 2,
        "Career Goal": goal is not None,
    }
    pct = round(sum(checks.values()) / len(checks) * 100)
    color = COLORS["success"] if pct >= 80 else (COLORS["warning"] if pct >= 50 else COLORS["danger"])
    st.markdown("---")
    st.markdown("### 📊 Profile Completion")
    st.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:10px;padding:1rem;">
  <div style="display:flex;justify-content:space-between;margin-bottom:0.4rem;">
    <span style="color:#F1F5F9;font-weight:600;">Completion</span>
    <span style="color:{color};font-weight:bold;">{pct}%</span>
  </div>
  <div style="background:#0F172A;border-radius:6px;height:10px;margin-bottom:0.6rem;">
    <div style="background:{color};height:10px;border-radius:6px;width:{pct}%;"></div>
  </div>
  {"".join(f'<div style="color:{"#10B981" if v else "#94A3B8"};font-size:0.82rem;padding:1px 0;">{"✅" if v else "⬜"} {k}</div>' for k,v in checks.items())}
</div>
""", unsafe_allow_html=True)
