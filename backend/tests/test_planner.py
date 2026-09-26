import datetime
from app.schemas import (
    GapItem,
    MatchResponse,
    OpportunityAnalysisData,
    OpportunityAnalyzeResponse,
    PlanRequest,
    StudentProfile,
)
from app.services.matcher import calculate_match
from app.services.planner import calculate_deadline_status, generate_action_plan


def make_plan_request(
    gaps=None,
    needs_verification=None,
    matched=None,
    deadline=None,
) -> PlanRequest:
    return PlanRequest(
        gaps=gaps or [],
        needs_verification=needs_verification or [],
        matched=matched or [],
        deadline=deadline,
    )


# 1. Missing skill generates an action
def test_missing_skill_generates_action():
    req = make_plan_request(
        gaps=[
            GapItem(
                category="Skill",
                requirement="Leadership",
                status="Missing",
                message="'Leadership' is missing from profile.",
            ),
            GapItem(
                category="Skill",
                requirement="Communication",
                status="Missing",
                message="'Communication' is missing from profile.",
            ),
        ]
    )
    plan = generate_action_plan(req)

    assert len(plan.priority_actions) == 2
    req_names = [a.requirement for a in plan.priority_actions]
    assert "Leadership" in req_names
    assert "Communication" in req_names

    leadership_act = next(a for a in plan.priority_actions if a.requirement == "Leadership")
    assert "leadership" in leadership_act.action.lower() or "organisasi" in leadership_act.action.lower()
    assert leadership_act.priority in ["High", "Medium"]


# 2. Missing document generates document preparation action
def test_missing_document_generates_action():
    req = make_plan_request(
        gaps=[
            GapItem(
                category="Document",
                requirement="Curriculum Vitae (CV) / Resume",
                status="Missing",
                message="'CV' is required.",
            ),
            GapItem(
                category="Document",
                requirement="Academic Transcript",
                status="Missing",
                message="'Transcript' is required.",
            ),
        ]
    )
    plan = generate_action_plan(req)

    cv_act = next((a for a in plan.priority_actions if "cv" in a.requirement.lower()), None)
    assert cv_act is not None
    assert cv_act.priority == "High"
    assert "cv" in cv_act.action.lower()

    trans_act = next((a for a in plan.priority_actions if "transcript" in a.requirement.lower()), None)
    assert trans_act is not None
    assert trans_act.priority == "High"
    assert "transkrip" in trans_act.action.lower()


# 3. Needs Verification creates verification action, not failure
def test_needs_verification_creates_verification_action_not_failure():
    req = make_plan_request(
        gaps=[],
        needs_verification=[
            GapItem(
                category="Eligibility",
                requirement="Indonesian Citizen (WNI)",
                status="Needs Verification",
                message="Requires external documentation.",
            ),
            GapItem(
                category="Eligibility",
                requirement="Open to all study programs / majors",
                status="Needs Verification",
                message="Check major coverage.",
            ),
        ],
    )
    plan = generate_action_plan(req)

    # Must be in verification_actions, NOT treated as a missing priority failure
    assert len(plan.verification_actions) == 2
    verify_reqs = [v.requirement for v in plan.verification_actions]
    assert "Indonesian Citizen (WNI)" in verify_reqs
    assert "Open to all study programs / majors" in verify_reqs

    wni_action = next(v for v in plan.verification_actions if "wni" in v.requirement.lower())
    assert "kewarganegaraan" in wni_action.action.lower() or "ktp" in wni_action.action.lower()
    assert wni_action.status == "todo"


# 4. Equivalent requirements do not create duplicate actions
def test_equivalent_requirements_no_duplicate_actions():
    req = make_plan_request(
        gaps=[
            GapItem(
                category="Document",
                requirement="Curriculum Vitae (CV) / Resume",
                status="Missing",
                message="CV required.",
            ),
            GapItem(
                category="Document",
                requirement="CV",
                status="Missing",
                message="CV required.",
            ),
            GapItem(
                category="Document",
                requirement="Resume",
                status="Missing",
                message="Resume required.",
            ),
        ],
        needs_verification=[
            GapItem(
                category="Eligibility",
                requirement="Indonesian Citizen (WNI)",
                status="Needs Verification",
                message="WNI check.",
            ),
            GapItem(
                category="Eligibility",
                requirement="Warga Negara Indonesia (WNI)",
                status="Needs Verification",
                message="WNI check.",
            ),
        ],
    )
    plan = generate_action_plan(req)

    # CV/Resume should produce exactly 1 priority action
    cv_actions = [a for a in plan.priority_actions if any(k in a.requirement.lower() for k in ["cv", "resume"])]
    assert len(cv_actions) == 1

    # WNI should produce exactly 1 verification action
    wni_actions = [v for v in plan.verification_actions if "wni" in v.requirement.lower() or "citizen" in v.requirement.lower()]
    assert len(wni_actions) == 1


# 5. Recommendation letter receives high priority / external coordination
def test_recommendation_letter_high_priority_and_next_best_action():
    req = make_plan_request(
        gaps=[
            GapItem(
                category="Skill",
                requirement="Leadership",
                status="Missing",
                message="Leadership missing.",
            ),
            GapItem(
                category="Document",
                requirement="Recommendation Letter",
                status="Missing",
                message="Recommendation letter required.",
            ),
        ]
    )
    plan = generate_action_plan(req)

    rec_act = next(a for a in plan.priority_actions if "recommendation" in a.requirement.lower() or "rekomendasi" in a.requirement.lower())
    assert rec_act.priority == "High"
    assert "dosen" in rec_act.action.lower() or "pembimbing" in rec_act.action.lower()

    # Next best action should specifically advise contacting lecturer/mentor first
    assert "rekomendasi" in plan.next_best_action.lower() or "dosen" in plan.next_best_action.lower()


# 6. Deadline parsing produces remaining-days status when valid
def test_deadline_produces_remaining_days_when_valid():
    future_year = datetime.date.today().year + 1
    valid_deadline = f"15 Oktober {future_year}"
    status_str, days = calculate_deadline_status(valid_deadline)

    assert days is not None
    assert days > 0
    assert "days remaining" in status_str

    req = make_plan_request(deadline=valid_deadline)
    plan = generate_action_plan(req)
    assert "days remaining" in plan.deadline_status


# 7. Unknown deadline does not fabricate remaining days
def test_unknown_deadline_does_not_fabricate_days():
    unparseable = "Kapan saja sebelum kuota program penuh tahun ini."
    status_str, days = calculate_deadline_status(unparseable)

    assert days is None
    assert "could not be reliably determined" in status_str

    none_status, none_days = calculate_deadline_status(None)
    assert none_days is None
    assert "No deadline specified" in none_status

    req = make_plan_request(deadline=unparseable)
    plan = generate_action_plan(req)
    assert plan.deadline_status == "Deadline could not be reliably determined."


# 8. next_best_action is deterministic
def test_next_best_action_deterministic():
    # Scenario A: Has Recommendation Letter -> must pick recommendation letter
    req_a = make_plan_request(
        gaps=[
            GapItem(category="Document", requirement="Recommendation Letter", status="Missing", message="req"),
            GapItem(category="Skill", requirement="Python", status="Missing", message="req"),
        ]
    )
    plan_a1 = generate_action_plan(req_a)
    plan_a2 = generate_action_plan(req_a)
    assert plan_a1.next_best_action == plan_a2.next_best_action
    assert "rekomendasi" in plan_a1.next_best_action.lower()

    # Scenario B: No Recommendation letter, but has Eligibility blocker
    req_b = make_plan_request(
        gaps=[
            GapItem(category="Eligibility", requirement="Teknik Informatika only", status="Missing", message="req"),
            GapItem(category="Skill", requirement="React", status="Missing", message="req"),
        ]
    )
    plan_b = generate_action_plan(req_b)
    assert "kelayakan" in plan_b.next_best_action.lower() or "syarat" in plan_b.next_best_action.lower()

    # Scenario C: Only Skill gap
    req_c = make_plan_request(
        gaps=[
            GapItem(category="Skill", requirement="Leadership", status="Missing", message="req"),
        ]
    )
    plan_c = generate_action_plan(req_c)
    assert "leadership" in plan_c.next_best_action.lower()


# 9. Empty gaps still produces a sensible plan
def test_empty_gaps_produces_sensible_plan():
    req = make_plan_request(gaps=[], needs_verification=[])
    plan = generate_action_plan(req)

    assert len(plan.priority_actions) == 0
    assert len(plan.verification_actions) == 0
    assert len(plan.summary) > 10
    assert "memenuhi" in plan.summary.lower() or "keselarasan" in plan.summary.lower()
    assert len(plan.next_best_action) > 10
    assert "pendaftaran" in plan.next_best_action.lower() or "submit" in plan.next_best_action.lower()


# 10. End-to-end integration with calculate_match
def test_end_to_end_matcher_and_planner_integration():
    future_year = datetime.date.today().year + 1
    opp = OpportunityAnalyzeResponse(
        opportunity_type="Scholarship",
        analysis=OpportunityAnalysisData(
            deadline=f"20 November {future_year}",
            minimum_gpa="3.25",
            semester_requirement="Minimal Semester 5",
            required_skills=["Python", "Leadership"],
            required_documents=["Curriculum Vitae (CV) / Resume", "Recommendation Letter"],
            benefits=["Full Tuition", "Monthly Stipend"],
            eligibility=["Mahasiswa aktif S1", "Indonesian Citizen (WNI)"],
        ),
    )
    profile = StudentProfile(
        study_program="Informatics Engineering",
        semester=5,
        gpa=3.52,
        skills=["Python"],  # Missing Leadership
        experience="Built web applications.",
    )
    match_result = calculate_match(profile, opp)

    # Pass match_result directly into PlanRequest
    plan_req = PlanRequest(
        match_result=match_result,
        opportunity=opp,
    )
    plan = generate_action_plan(plan_req)

    assert plan.summary is not None
    assert len(plan.priority_actions) >= 1

    # Should identify missing Leadership
    prio_reqs = [a.requirement for a in plan.priority_actions]
    assert "Leadership" in prio_reqs

    # Should identify Recommendation Letter
    assert any("recommendation" in r.lower() or "rekomendasi" in r.lower() for r in prio_reqs)

    # WNI should be in verification checklist
    verify_reqs = [v.requirement for v in plan.verification_actions]
    assert any("wni" in r.lower() or "citizen" in r.lower() for r in verify_reqs)

    # Deadline status should be upcoming
    assert "days remaining" in plan.deadline_status
