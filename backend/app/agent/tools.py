from typing import Optional
from app.schemas import (
    ActionPlanResponse,
    MatchResponse,
    OpportunityAnalysisData,
    OpportunityAnalyzeResponse,
    PlanRequest,
    StudentProfile,
)
from app.services.analyzer import analyze_opportunity
from app.services.matcher import calculate_match
from app.services.planner import generate_action_plan


def analyze_opportunity_tool(
    opportunity_type: str, description: str
) -> OpportunityAnalyzeResponse:
    """
    Action 1: Deterministically extracts requirements, deadlines, GPA, skills,
    documents, and benefits from an opportunity description.
    Wraps existing analyzer.py without duplicating logic.
    """
    raw_result = analyze_opportunity(
        opportunity_type=opportunity_type, description=description
    )
    if isinstance(raw_result, OpportunityAnalyzeResponse):
        return raw_result
    return OpportunityAnalyzeResponse(
        opportunity_type=raw_result.get("opportunity_type", opportunity_type),
        analysis=OpportunityAnalysisData(**raw_result.get("analysis", {})),
    )


def evaluate_profile_tool(
    profile: StudentProfile, opportunity: OpportunityAnalyzeResponse
) -> MatchResponse:
    """
    Action 2: Evaluates student profile readiness against structured opportunity requirements.
    Wraps existing matcher.py without duplicating scoring or matching logic.
    """
    return calculate_match(profile=profile, opportunity=opportunity)


def build_action_plan_tool(
    match_result: MatchResponse,
    opportunity: OpportunityAnalyzeResponse,
    deadline: Optional[str] = None,
) -> ActionPlanResponse:
    """
    Action 3: Generates prioritized action steps and a verification checklist.
    Wraps existing planner.py without duplicating prioritization logic.
    """
    effective_deadline = deadline or opportunity.analysis.deadline
    plan_request = PlanRequest(
        match_result=match_result,
        opportunity=opportunity,
        gaps=match_result.gaps,
        needs_verification=match_result.needs_verification,
        matched=match_result.matched,
        deadline=effective_deadline,
    )
    return generate_action_plan(plan_request)
