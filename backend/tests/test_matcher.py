import datetime
from app.schemas import (
    OpportunityAnalysisData,
    OpportunityAnalyzeResponse,
    StudentProfile,
)
from app.services.matcher import calculate_match


def make_test_opportunity(
    minimum_gpa=None,
    semester_requirement=None,
    required_skills=None,
    required_documents=None,
    deadline=None,
    eligibility=None,
    opportunity_type="Scholarship",
) -> OpportunityAnalyzeResponse:
    return OpportunityAnalyzeResponse(
        opportunity_type=opportunity_type,
        analysis=OpportunityAnalysisData(
            deadline=deadline,
            minimum_gpa=minimum_gpa,
            semester_requirement=semester_requirement,
            required_skills=required_skills or [],
            required_documents=required_documents or [],
            benefits=[],
            eligibility=eligibility or [],
        ),
    )


# 1. GPA above minimum
def test_gpa_above_minimum():
    opp = make_test_opportunity(minimum_gpa="3.25")
    profile = StudentProfile(gpa=3.52)
    res = calculate_match(profile, opp)

    assert res.breakdown.academic.status == "matched"
    assert res.breakdown.academic.score == 20.0
    assert any("meets or exceeds" in m.message for m in res.matched)


# 2. GPA below minimum
def test_gpa_below_minimum():
    opp = make_test_opportunity(minimum_gpa="3.25")
    profile = StudentProfile(gpa=2.80)
    res = calculate_match(profile, opp)

    assert res.breakdown.academic.status == "missing"
    assert res.breakdown.academic.score == 0.0
    assert any("below the required minimum" in g.message for g in res.gaps)


# 3. Semester satisfies requirement
def test_semester_satisfies_requirement():
    opp = make_test_opportunity(semester_requirement="Minimal Semester 5")
    profile = StudentProfile(semester=5)
    res = calculate_match(profile, opp)

    assert res.breakdown.academic.status == "matched"
    assert res.breakdown.academic.score == 20.0
    assert any("meets the minimum requirement" in m.message for m in res.matched)


# 4. Semester fails requirement
def test_semester_fails_requirement():
    opp = make_test_opportunity(semester_requirement="Minimal Semester 5")
    profile = StudentProfile(semester=3)
    res = calculate_match(profile, opp)

    assert res.breakdown.academic.status == "missing"
    assert res.breakdown.academic.score == 0.0
    assert any("below the minimum requirement" in g.message for g in res.gaps)


# 5. Partial skill match
def test_partial_skill_match():
    opp = make_test_opportunity(required_skills=["Python", "React", "Docker"])
    profile = StudentProfile(skills=["Python", "React"])
    res = calculate_match(profile, opp)

    assert res.breakdown.skills.status == "partial"
    assert res.breakdown.skills.score == 10.0  # (2/3) * 15 = 10.0
    assert any(g.requirement == "Docker" for g in res.gaps)


# 6. Full skill match
def test_full_skill_match():
    opp = make_test_opportunity(required_skills=["Python", "React"])
    profile = StudentProfile(skills=["Python", "React", "Node.js"])
    res = calculate_match(profile, opp)

    assert res.breakdown.skills.status == "matched"
    assert res.breakdown.skills.score == 15.0
    assert not any(g.category == "Skill" for g in res.gaps)


# 7. No required skills
def test_no_required_skills():
    opp = make_test_opportunity(required_skills=[])
    profile = StudentProfile(skills=["Python", "React"])
    res = calculate_match(profile, opp)

    assert res.breakdown.skills.status == "not_specified"
    assert res.breakdown.skills.score is None


# 8. Unknown/unverifiable criteria are NOT treated as automatic failure
def test_unknown_unverifiable_criteria_not_penalized():
    opp = make_test_opportunity(
        minimum_gpa="3.00",
        required_documents=["Curriculum Vitae (CV) / Resume", "Academic Transcript"],
        eligibility=["Indonesian Citizen (WNI)"],
    )
    # Student satisfies GPA, but docs and citizenship cannot be directly scored
    profile = StudentProfile(gpa=3.80)
    res = calculate_match(profile, opp)

    # Documents and WNI must be in needs_verification
    assert res.breakdown.documents.status == "needs_verification"
    assert res.breakdown.documents.score is None
    assert any(item.category == "Document" for item in res.needs_verification)
    assert any(item.requirement == "Indonesian Citizen (WNI)" for item in res.needs_verification)

    # Student should have high score because only evaluable criterion (GPA) passed
    assert res.match_score == 100


# 9. Final score stays between 0 and 100
def test_final_score_stays_between_0_and_100():
    # Failing scenario
    opp_fail = make_test_opportunity(
        minimum_gpa="3.50",
        semester_requirement="Minimal Semester 5",
        required_skills=["Rust", "Kubernetes"],
    )
    prof_fail = StudentProfile(gpa=2.00, semester=2, skills=["HTML"])
    res_fail = calculate_match(prof_fail, opp_fail)
    assert 0 <= res_fail.match_score <= 100
    assert res_fail.match_score == 0

    # Passing scenario
    future_year = datetime.date.today().year + 1
    opp_pass = make_test_opportunity(
        minimum_gpa="3.00",
        semester_requirement="Minimal Semester 3",
        required_skills=["Python"],
        deadline=f"15 Oktober {future_year}",
    )
    prof_pass = StudentProfile(gpa=3.90, semester=5, skills=["Python"])
    res_pass = calculate_match(prof_pass, opp_pass)
    assert 0 <= res_pass.match_score <= 100
    assert res_pass.match_score == 100


# 10. Realistic scholarship matching scenario
def test_realistic_scholarship_scenario():
    future_year = datetime.date.today().year + 1
    opp = make_test_opportunity(
        opportunity_type="Scholarship",
        minimum_gpa="3.25",
        semester_requirement="Minimal Semester 5",
        required_skills=["Python", "Leadership"],
        required_documents=["Curriculum Vitae (CV) / Resume", "Academic Transcript"],
        deadline=f"15 Oktober {future_year}",
        eligibility=["Mahasiswa aktif S1", "Indonesian Citizen (WNI)"],
    )
    profile = StudentProfile(
        study_program="Informatics Engineering",
        semester=5,
        gpa=3.52,
        skills=["Python", "React"],
        experience="Led university student association project.",
    )
    res = calculate_match(profile, opp)

    # Score should be strong (around 90-95%)
    assert 80 <= res.match_score <= 100
    assert "Profile Match" not in res.summary  # summary is descriptive
    assert len(res.summary) > 10

    # Check breakdown
    assert res.breakdown.academic.status == "matched"
    assert res.breakdown.deadline.status == "upcoming"
    assert res.breakdown.documents.status == "needs_verification"

    # Check gaps: only missing skill should be Leadership if not detected
    # (Notice "Leadership" is present in experience! So it might match, or if it matched, 0 gaps)
    missing_reqs = [g.requirement for g in res.gaps]
    assert "Minimum GPA 3.25" not in missing_reqs

    # Documents and WNI must be in needs_verification
    verify_reqs = [item.requirement for item in res.needs_verification]
    assert "Curriculum Vitae (CV) / Resume" in verify_reqs
    assert "Indonesian Citizen (WNI)" in verify_reqs


def test_matcher_no_duplicate_needs_verification():
    # Pass an opportunity that has overlapping eligibility items and evaluated fields
    opp = make_test_opportunity(
        minimum_gpa="3.25",
        semester_requirement="Minimal Semester 5",
        required_skills=["Python"],
        required_documents=["Curriculum Vitae (CV) / Resume"],
        eligibility=[
            "Mahasiswa aktif S1",
            "Mahasiswa aktif S1 minimal semester 5",
            "Warga Negara Indonesia (WNI)",
            "Indonesian Citizen (WNI)",
            "Minimum GPA of 3.25",
            "Enrolled in Minimal Semester 5",
        ],
    )
    profile = StudentProfile(
        study_program="Informatics Engineering",
        semester=5,
        gpa=3.52,
        skills=["Python"],
    )
    res = calculate_match(profile, opp)

    # 1. GPA, Semester, and Active Student are matched from profile
    matched_reqs = [m.requirement for m in res.matched]
    assert any("GPA" in r or "3.25" in r for r in matched_reqs)
    assert any("Semester" in r for r in matched_reqs)
    assert any("Mahasiswa aktif" in r for r in matched_reqs)

    # 2. Needs verification should NOT contain GPA, Semester, or Active Student
    verify_reqs = [v.requirement for v in res.needs_verification]
    assert not any("gpa" in r.lower() or "ipk" in r.lower() for r in verify_reqs)
    assert not any("semester" in r.lower() for r in verify_reqs)
    assert not any("mahasiswa aktif" in r.lower() for r in verify_reqs)

    # 3. WNI should only appear ONCE in needs_verification
    wni_in_verify = [r for r in verify_reqs if "wni" in r.lower() or "citizen" in r.lower()]
    assert len(wni_in_verify) == 1

    # 4. Total needs_verification should be concise (only Document + 1 Citizenship)
    assert len(res.needs_verification) == 2

