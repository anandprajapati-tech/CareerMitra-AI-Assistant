"""CareerMitra AI – Validation Suite"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run():
    print("=== CareerMitra AI – Validation Suite ===")

    # 1. Config
    print("\n[1] Config module...")
    from src.config import (APP_NAME, IBM_WATSONX_URL, GRANITE_MODEL_ID,
                             ibm_configured, PAGES, CAREER_DOMAINS)
    print(f"    APP_NAME         : {APP_NAME}")
    print(f"    IBM_WATSONX_URL  : {IBM_WATSONX_URL}")
    print(f"    GRANITE_MODEL_ID : {GRANITE_MODEL_ID}")
    print(f"    ibm_configured() : {ibm_configured()}")
    print(f"    Pages            : {len(PAGES)} pages defined")
    print(f"    Career domains   : {len(CAREER_DOMAINS)} domains")
    assert "au-syd" in IBM_WATSONX_URL, "FAIL: URL not au-syd"
    print("    PASS")

    # 2. Database
    print("\n[2] Database module...")
    from src.database import (
        init_db, save_student, get_student_by_id, save_skills, get_skills,
        save_interests, get_interests, save_career_goal, get_career_goal,
        save_milestones, get_milestones, update_milestone_status,
        get_chat_history, save_chat_message, clear_chat_history,
        save_recommendation, get_latest_recommendation, get_student_by_email,
    )
    init_db()
    sid = save_student({
        "name": "Test User", "email": "test_ci@example.com", "age": 20,
        "city": "Pune", "education": "Bachelor's Degree",
        "stream": "Computer Science", "institution": "Test College", "gpa": 8.5,
    })
    assert sid and sid > 0
    student = get_student_by_id(sid)
    assert student and student["name"] == "Test User"
    by_email = get_student_by_email("test_ci@example.com")
    assert by_email is not None
    save_skills(sid, [
        {"name": "Python",          "category": "Technical", "proficiency": "Advanced"},
        {"name": "SQL",             "category": "Technical", "proficiency": "Intermediate"},
        {"name": "Machine Learning","category": "Technical", "proficiency": "Beginner"},
    ])
    skills = get_skills(sid)
    assert len(skills) >= 3
    save_interests(sid, ["Programming & Coding", "Mathematics & Statistics"])
    interests = get_interests(sid)
    assert len(interests) >= 2
    save_career_goal(sid, {
        "domain": "Data Science & AI/ML", "role": "Data Scientist",
        "timeline": "2 years", "notes": "my goal",
    })
    goal = get_career_goal(sid)
    assert goal and goal["goal_domain"] == "Data Science & AI/ML"
    save_milestones(sid, [
        {"title": "Learn Pandas", "category": "Skill Development", "completed": False, "due_date": None},
    ])
    ms = get_milestones(sid)
    assert len(ms) >= 1
    update_milestone_status(ms[0]["id"], True)
    ms2 = get_milestones(sid)
    assert ms2[0]["completed"] == 1
    save_chat_message(sid, "user", "Hello")
    save_chat_message(sid, "assistant", "Hi there!")
    hist = get_chat_history(sid)
    assert len(hist) >= 2
    clear_chat_history(sid)
    assert len(get_chat_history(sid)) == 0
    save_recommendation(sid, {
        "domain": "Data Science & AI/ML", "roles": ["Data Scientist"],
        "score": 72.5, "reasoning": "test",
    })
    rec = get_latest_recommendation(sid)
    assert rec and rec["career_domain"] == "Data Science & AI/ML"
    print("    PASS")

    # 3. Career recommendation engine
    print("\n[3] Career recommendation engine...")
    from src.career_recommendation import rank_domains, get_top_recommendations
    test_skills    = [
        {"skill_name": "Python",          "proficiency": "Advanced"},
        {"skill_name": "Machine Learning","proficiency": "Advanced"},
        {"skill_name": "SQL",             "proficiency": "Advanced"},
        {"skill_name": "Statistical Analysis", "proficiency": "Intermediate"},
    ]
    test_interests = ["Programming & Coding", "Mathematics & Statistics"]
    ranked = rank_domains(test_skills, test_interests, "Computer Science")
    assert len(ranked) > 0
    top3 = get_top_recommendations(test_skills, test_interests, "Computer Science", top_n=3)
    assert len(top3) == 3
    top_domains = [r["domain"] for r in top3]
    assert "Data Science & AI/ML" in top_domains, f"Expected DS in top3, got {top_domains}"
    print(f"    Top 3 domains: {top_domains}")
    print("    PASS")

    # 4. Skill gap analysis
    print("\n[4] Skill gap analysis engine...")
    from src.skill_gap_analysis import compute_gap, readiness_score, missing_skills, available_domains
    gap = compute_gap(test_skills, "Data Science & AI/ML")
    assert "Python" in gap
    # With Advanced proficiency (75) and required 75 --> gap == 0 --> Met
    assert gap["Python"]["gap"] == 0, f"Got gap={gap['Python']['gap']}"
    rs = readiness_score(gap)
    ms_list = missing_skills(gap)
    print(f"    Readiness: {rs}%  |  Missing: {ms_list}")
    domains = available_domains()
    assert len(domains) >= 8
    print("    PASS")

    # 5. Career roadmap
    print("\n[5] Career roadmap module...")
    from src.career_roadmap import get_roadmap, available_domains as rd_domains, get_phase_milestones
    roadmap = get_roadmap("Data Science & AI/ML")
    assert len(roadmap) == 4
    assert len(roadmap[0]["milestones"]) > 0
    ms_p0 = get_phase_milestones("Technology & Engineering", 0)
    assert len(ms_p0) > 0
    all_domains = rd_domains()
    assert len(all_domains) >= 7
    print(f"    {len(all_domains)} domain roadmaps available")
    print("    PASS")

    # 6. Progress tracking
    print("\n[6] Progress tracking module...")
    from src.progress_tracking import (
        profile_completion, milestone_progress, full_summary, add_milestone,
    )
    comp = profile_completion(sid)
    assert "pct" in comp and comp["pct"] >= 60
    ms_prog = milestone_progress(sid)
    assert "total" in ms_prog and ms_prog["total"] >= 1
    new_ms = add_milestone(sid, "Complete Kaggle Competition", "Project")
    assert len(new_ms) >= 2
    summary = full_summary(sid)
    assert summary["student"] and summary["profile_completion"]["pct"] >= 60
    print(f"    Profile: {comp['pct']}%  |  Milestones: {ms_prog['total']}")
    print("    PASS")

    # 7. IBM Granite module
    print("\n[7] IBM Granite module...")
    from src.ibm_granite import (
        granite_chat, granite_skill_gap_analysis,
        granite_roadmap, granite_career_recommendations, get_model_error,
    )
    response = granite_chat("Name: Test | Education: B.Tech", [], "What career suits me?")
    assert isinstance(response, str) and len(response) > 50
    sg = granite_skill_gap_analysis("Data Science & AI/ML", ["Python"], ["Python", "Machine Learning", "SQL"])
    assert isinstance(sg, str) and len(sg) > 10
    rm = granite_roadmap("Data Science & AI/ML", "Data Scientist", "2 years", ["Python"])
    assert isinstance(rm, str) and len(rm) > 10
    cr = granite_career_recommendations("Bachelor's Degree", "Computer Science",
                                        ["Python"], ["Programming & Coding"])
    assert isinstance(cr, str)
    err = get_model_error()
    if err:
        print(f"    IBM Granite config error: {err[:120]}")
    else:
        print("    IBM Granite connected OK")
    print("    PASS (demo mode responses work)")

    # 8. Import all page modules
    print("\n[8] Page modules import check...")
    from src.pages.home               import render_home
    from src.pages.student_profile    import render_student_profile
    from src.pages.ai_counselor       import render_ai_counselor
    from src.pages.career_recommendations import render_career_recommendations
    from src.pages.skill_gap          import render_skill_gap_analysis
    from src.pages.roadmap            import render_career_roadmap
    from src.pages.job_market         import render_job_market_insights
    from src.pages.dashboard          import render_dashboard
    print("    All 8 page modules imported successfully")
    print("    PASS")

    print("\n" + "=" * 50)
    print("ALL 8 TESTS PASSED")
    print("=" * 50)

if __name__ == "__main__":
    run()
