from unittest.mock import MagicMock
import pytest

from app.agent.grounding import validate_and_sanitize_personalization
from app.agent.orchestrator import SkillBridgeAgent
from app.agent.tools import (
    analyze_opportunity_tool,
    build_action_plan_tool,
    evaluate_profile_tool,
)
from app.routes.opportunities import agent_analyze
from app.schemas import (
    AgentAnalyzeRequest,
    AgentAnalyzeResponse,
    OpportunityAnalyzeResponse,
    StudentProfile,
)
from app.services.analyzer import analyze_opportunity
from app.services.matcher import calculate_match
from app.services.planner import generate_action_plan, PlanRequest


@pytest.fixture
def sample_profile():
    return StudentProfile(
        study_program="Informatics Engineering",
        semester=5,
        gpa=3.52,
        skills=["Python", "React", "Cloud Computing"],
        experience="Software engineer intern at university lab, actively involved in student council.",
    )


@pytest.fixture
def sample_opportunity_text():
    return """
    Beasiswa Prestasi Unggulan 2026
    Program beasiswa untuk mahasiswa aktif S1 minimal semester 5 dengan IPK minimal 3.25.
    Keahlian yang dibutuhkan: Python, Leadership, and Communication.
    Kirimkan CV, transkrip nilai, dan surat rekomendasi.
    Pendaftaran dibuka sampai 15 Oktober 2026.
    Fasilitas mencakup bantuan UKT penuh dan tunjangan bulanan.
    """


# 1. Agent calls analyzer action
def test_agent_calls_analyzer_action(sample_profile, sample_opportunity_text):
    mock_llm = MagicMock(return_value=None)
    agent = SkillBridgeAgent(llm_provider=mock_llm)

    res = agent.run(
        profile=sample_profile,
        opportunity_type="Scholarship",
        description=sample_opportunity_text,
    )

    assert "analyze_opportunity" in res.agent.actions_executed
    assert res.analysis.opportunity_type == "Scholarship"
    assert res.analysis.analysis.minimum_gpa == "3.25"
    assert "Python" in res.analysis.analysis.required_skills


# 2. Agent calls matcher action
def test_agent_calls_matcher_action(sample_profile, sample_opportunity_text):
    mock_llm = MagicMock(return_value=None)
    agent = SkillBridgeAgent(llm_provider=mock_llm)

    res = agent.run(
        profile=sample_profile,
        opportunity_type="Scholarship",
        description=sample_opportunity_text,
    )

    assert "evaluate_profile" in res.agent.actions_executed
    assert res.match.match_score > 0
    assert res.match.breakdown.academic.status == "matched"
    assert len(res.match.matched) > 0


# 3. Agent calls planner action
def test_agent_calls_planner_action(sample_profile, sample_opportunity_text):
    mock_llm = MagicMock(return_value=None)
    agent = SkillBridgeAgent(llm_provider=mock_llm)

    res = agent.run(
        profile=sample_profile,
        opportunity_type="Scholarship",
        description=sample_opportunity_text,
    )

    assert "build_action_plan" in res.agent.actions_executed
    assert res.plan.next_best_action is not None
    assert len(res.plan.next_best_action) > 0
    assert len(res.plan.priority_actions) > 0


# 4. actions_executed contains at least 2 distinct actions (all 3 verified)
def test_actions_executed_contains_all_actions(sample_profile, sample_opportunity_text):
    mock_llm = MagicMock(return_value=None)
    agent = SkillBridgeAgent(llm_provider=mock_llm)

    res = agent.run(
        profile=sample_profile,
        opportunity_type="Scholarship",
        description=sample_opportunity_text,
    )

    assert len(res.agent.actions_executed) >= 3
    assert res.agent.actions_executed == [
        "analyze_opportunity",
        "evaluate_profile",
        "build_action_plan",
    ]


# 5. Deterministic values remain completely unchanged by the agent
def test_deterministic_values_remain_unchanged(sample_profile, sample_opportunity_text):
    # Standalone executions
    direct_analysis_raw = analyze_opportunity("Scholarship", sample_opportunity_text)
    direct_analysis = OpportunityAnalyzeResponse(
        opportunity_type="Scholarship",
        analysis=direct_analysis_raw["analysis"],
    )
    direct_match = calculate_match(sample_profile, direct_analysis)
    direct_plan = generate_action_plan(
        PlanRequest(
            match_result=direct_match,
            opportunity=direct_analysis,
            gaps=direct_match.gaps,
            needs_verification=direct_match.needs_verification,
            matched=direct_match.matched,
            deadline=direct_analysis.analysis.deadline,
        )
    )

    # Agent execution
    mock_llm = MagicMock(return_value=None)
    agent = SkillBridgeAgent(llm_provider=mock_llm)
    res = agent.run(sample_profile, "Scholarship", sample_opportunity_text)

    # Verify exact parity
    assert res.analysis.analysis.minimum_gpa == direct_analysis.analysis.minimum_gpa
    assert res.analysis.analysis.deadline == direct_analysis.analysis.deadline
    assert res.analysis.analysis.required_skills == direct_analysis.analysis.required_skills
    assert res.match.match_score == direct_match.match_score
    assert len(res.match.gaps) == len(direct_match.gaps)
    assert len(res.match.matched) == len(direct_match.matched)
    assert res.plan.next_best_action == direct_plan.next_best_action
    assert len(res.plan.priority_actions) == len(direct_plan.priority_actions)


# 6. AI receives grounded structured context containing only verified facts
def test_ai_receives_grounded_structured_context(sample_profile, sample_opportunity_text):
    captured_context = {}

    def mock_llm_capture(context):
        nonlocal captured_context
        captured_context = context
        return {
            "summary": "Solid student readiness with specific gaps to resolve.",
            "why_this_match": "Academic prerequisites are fully met.",
            "focus_areas": ["Leadership evidence"],
            "recommended_strategy": "Request recommendation letter early.",
            "encouragement": "You are well-positioned with targeted preparation.",
        }

    agent = SkillBridgeAgent(llm_provider=mock_llm_capture)
    res = agent.run(sample_profile, "Scholarship", sample_opportunity_text)

    assert "student_profile" in captured_context
    assert captured_context["student_profile"]["gpa"] == 3.52
    assert "opportunity_criteria" in captured_context
    assert captured_context["opportunity_criteria"]["minimum_gpa"] == "3.25"
    assert "profile_match_results" in captured_context
    assert captured_context["profile_match_results"]["match_score"] == res.match.match_score
    assert "action_plan_summary" in captured_context

    assert res.agent.ai_personalization_available is True
    assert res.agent.personalization is not None
    assert res.agent.personalization.summary == "Solid student readiness with specific gaps to resolve."


# 7. Missing API key falls back safely without failing deterministic results
def test_missing_api_key_falls_back_safely(sample_profile, sample_opportunity_text):
    # LLM provider returns None when key is absent
    agent = SkillBridgeAgent(llm_provider=lambda ctx: None)
    res = agent.run(sample_profile, "Scholarship", sample_opportunity_text)

    assert res.agent.ai_personalization_available is False
    assert res.agent.personalization is None
    # Deterministic pipeline succeeded completely
    assert res.match.match_score > 0
    assert len(res.plan.priority_actions) > 0


# 8. Provider failure (timeout, network error, exception) falls back safely
def test_provider_failure_falls_back_safely(sample_profile, sample_opportunity_text):
    def failing_provider(ctx):
        raise TimeoutError("Gemini API connection timed out after 10s")

    agent = SkillBridgeAgent(llm_provider=failing_provider)
    res = agent.run(sample_profile, "Scholarship", sample_opportunity_text)

    assert res.agent.ai_personalization_available is False
    assert res.agent.personalization is None
    # Deterministic results remain 100% accessible
    assert res.analysis is not None
    assert res.match is not None
    assert res.plan is not None


# 9. AI cannot break or alter deterministic response
def test_ai_cannot_break_deterministic_response(sample_profile, sample_opportunity_text):
    def rogue_ai_provider(ctx):
        return {
            "summary": "Fabricated claim: You have an 100% acceptance chance!",
            "why_this_match": "Invented reason",
            "focus_areas": ["None"],
            "recommended_strategy": "Do nothing",
            "encouragement": "Guaranteed selection",
        }

    agent = SkillBridgeAgent(llm_provider=rogue_ai_provider)
    res = agent.run(sample_profile, "Scholarship", sample_opportunity_text)

    # Core scores and criteria are strictly dictated by deterministic services
    assert res.match.match_score < 100
    assert res.analysis.analysis.minimum_gpa == "3.25"
    assert res.plan.next_best_action is not None
    assert "surat rekomendasi" in res.plan.next_best_action.lower() or "leadership" in res.plan.next_best_action.lower()


# 10. Endpoint test via route handler
def test_agent_analyze_endpoint_handler(sample_profile, sample_opportunity_text):
    payload = AgentAnalyzeRequest(
        profile=sample_profile,
        opportunity_type="Scholarship",
        description=sample_opportunity_text,
    )
    res = agent_analyze(payload)

    assert isinstance(res, AgentAnalyzeResponse)
    assert res.analysis.opportunity_type == "Scholarship"
    assert res.match.match_score > 0
    assert len(res.agent.actions_executed) == 3


# 11. Security check: API key is never exposed in response
def test_api_key_not_exposed_in_response(sample_profile, sample_opportunity_text):
    mock_llm = MagicMock(return_value=None)
    agent = SkillBridgeAgent(llm_provider=mock_llm)
    res = agent.run(sample_profile, "Scholarship", sample_opportunity_text)

    dumped = res.model_dump()
    dumped_str = str(dumped).lower()

    assert "api_key" not in dumped_str
    assert "gemini_api_key" not in dumped_str


# 12. State B: GEMINI_API_KEY available produces personalization
def test_gemini_available_returns_personalization(sample_profile, sample_opportunity_text):
    mock_llm_response = {
        "summary": "Solid student profile aligned with academic requirements.",
        "why_this_match": "Prerequisites for semester and GPA are met.",
        "focus_areas": ["Leadership evidence", "Communication project"],
        "recommended_strategy": "Request recommendation letter early.",
        "encouragement": "You have a strong foundation to apply.",
    }
    agent = SkillBridgeAgent(llm_provider=lambda ctx: mock_llm_response)
    res = agent.run(sample_profile, "Scholarship", sample_opportunity_text)

    assert res.agent.ai_personalization_available is True
    assert res.agent.personalization is not None
    assert res.agent.personalization.summary == mock_llm_response["summary"]
    assert res.agent.personalization.why_this_match == mock_llm_response["why_this_match"]
    assert res.agent.personalization.focus_areas == mock_llm_response["focus_areas"]
    assert res.agent.personalization.recommended_strategy == mock_llm_response["recommended_strategy"]
    assert res.agent.personalization.encouragement == mock_llm_response["encouragement"]


# 13. Document accuracy: Agent does not invent documents when none specified
def test_agent_opportunity_without_documents_does_not_invent_documents(sample_profile):
    opp_text_no_docs = """
    Software Engineering Challenge 2026
    Kualifikasi:
    - Mahasiswa aktif S1 minimal semester 4
    - IPK minimal 3.00
    - Menguasai Python dan React
    
    Benefit:
    - Sertifikat penyelesaian dan hadiah tunai
    """
    def rogue_ai_provider(ctx):
        return {
            "summary": "Profile summary",
            "why_this_match": "Good match",
            "focus_areas": ["Siapkan CV dan transkrip nilai", "Pelajari React testing"],
            "recommended_strategy": "Apply early",
            "encouragement": "Good luck!",
        }

    agent = SkillBridgeAgent(llm_provider=rogue_ai_provider)
    res = agent.run(sample_profile, "Competition", opp_text_no_docs)

    # 1. Analyzer returns required_documents = []
    assert res.analysis.analysis.required_documents == []

    # 2. Matcher treats documents as not_specified, not penalty
    assert res.match.breakdown.documents.status == "not_specified"
    assert res.match.breakdown.documents.score is None

    # 3. Planner does not invent document actions
    doc_priority = [a for a in res.plan.priority_actions if a.category == "Documents"]
    assert len(doc_priority) == 0

    # 4. Agent sanitizes hallucinated document focus areas
    assert res.agent.personalization is not None
    focus_areas = [f.lower() for f in res.agent.personalization.focus_areas]
    assert not any("cv" in f or "transkrip" in f for f in focus_areas)
    assert any("react" in f for f in focus_areas)


# 14. Direct Grounding Unit Test: Unsupported CV and transcript are stripped from focus areas
def test_grounding_removes_unsupported_cv_and_transcript():
    raw = {
        "focus_areas": [
            "Siapkan CV dan transkrip nilai",
            "Pelajari React testing",
        ]
    }

    result = validate_and_sanitize_personalization(
        raw,
        required_documents=[],
    )

    assert result["focus_areas"] == [
        "Pelajari React testing"
    ]


