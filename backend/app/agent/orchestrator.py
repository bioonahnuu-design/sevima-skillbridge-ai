import logging
from typing import Any, Callable, Dict, Optional

from app.agent.grounding import validate_and_sanitize_personalization
from app.agent.llm import generate_personalization
from app.agent.tools import (
    analyze_opportunity_tool,
    build_action_plan_tool,
    evaluate_profile_tool,
)
from app.schemas import (
    ActionPlanResponse,
    AgentAnalyzeResponse,
    AgentMeta,
    AIPersonalization,
    MatchResponse,
    OpportunityAnalyzeResponse,
    StudentProfile,
)

logger = logging.getLogger("skillbridge.agent.orchestrator")


class SkillBridgeAgent:
    """
    SkillBridge AI Agent Orchestrator.
    Coordinates deterministic analysis, profile matching, action planning,
    and grounded AI personalization while preserving deterministic engines
    as the sole source of truth.
    """

    def __init__(
        self,
        llm_provider: Optional[Callable[[Dict[str, Any]], Optional[Dict[str, Any]]]] = None,
    ):
        self.llm_provider = llm_provider or generate_personalization

    @staticmethod
    def build_grounded_context(
        profile: StudentProfile,
        analysis: OpportunityAnalyzeResponse,
        match: MatchResponse,
        plan: ActionPlanResponse,
    ) -> Dict[str, Any]:
        """
        Builds a strictly grounded context dictionary containing only pre-extracted
        facts and pre-calculated deterministic results.
        """
        analysis_data = analysis.analysis
        return {
            "student_profile": {
                "study_program": profile.study_program or "Not specified",
                "semester": profile.semester,
                "gpa": profile.gpa,
                "skills": profile.skills,
                "experience": profile.experience or "None provided",
            },
            "opportunity_criteria": {
                "opportunity_type": analysis.opportunity_type,
                "deadline": analysis_data.deadline or "Not specified",
                "minimum_gpa": analysis_data.minimum_gpa or "None specified",
                "semester_requirement": analysis_data.semester_requirement or "Open to all semesters",
                "required_skills": analysis_data.required_skills,
                "required_documents": analysis_data.required_documents,
                "eligibility": analysis_data.eligibility,
                "benefits": analysis_data.benefits,
            },
            "profile_match_results": {
                "match_score": match.match_score,
                "summary": match.summary,
                "matched_requirements": [
                    {"requirement": m.requirement, "category": m.category, "message": m.message}
                    for m in match.matched
                ],
                "requirement_gaps": [
                    {"requirement": g.requirement, "category": g.category, "message": g.message}
                    for g in match.gaps
                ],
                "needs_verification": [
                    {"requirement": v.requirement, "category": v.category, "message": v.message}
                    for v in match.needs_verification
                ],
            },
            "action_plan_summary": {
                "next_best_action": plan.next_best_action,
                "deadline_status": plan.deadline_status,
                "priority_actions": [
                    {
                        "priority": a.priority,
                        "category": a.category,
                        "requirement": a.requirement,
                        "action": a.action,
                        "reason": a.reason,
                    }
                    for a in plan.priority_actions[:5]
                ],
            },
        }

    def run(
        self,
        profile: StudentProfile,
        opportunity_type: str,
        description: str,
    ) -> AgentAnalyzeResponse:
        """
        Executes the three-phase deterministic tool orchestration followed by
        grounded AI personalization.
        """
        actions_executed = []

        # ACTION 1: analyze_opportunity
        actions_executed.append("analyze_opportunity")
        analysis_result: OpportunityAnalyzeResponse = analyze_opportunity_tool(
            opportunity_type=opportunity_type,
            description=description,
        )

        # ACTION 2: evaluate_profile
        actions_executed.append("evaluate_profile")
        match_result: MatchResponse = evaluate_profile_tool(
            profile=profile,
            opportunity=analysis_result,
        )

        # ACTION 3: build_action_plan
        actions_executed.append("build_action_plan")
        plan_result: ActionPlanResponse = build_action_plan_tool(
            match_result=match_result,
            opportunity=analysis_result,
            deadline=analysis_result.analysis.deadline,
        )

        # Grounded AI Personalization with guaranteed graceful fallback
        personalization_model: Optional[AIPersonalization] = None
        ai_available = False

        grounded_context = self.build_grounded_context(
            profile=profile,
            analysis=analysis_result,
            match=match_result,
            plan=plan_result,
        )

        try:
            raw_ai = self.llm_provider(grounded_context)
            if raw_ai and isinstance(raw_ai, dict):
                sanitized_ai = validate_and_sanitize_personalization(
                    raw_ai=raw_ai,
                    required_documents=analysis_result.analysis.required_documents,
                    grounded_context=grounded_context,
                )
                personalization_model = AIPersonalization(**sanitized_ai)
                ai_available = True
        except Exception as e:
            logger.warning("AI personalization fallback triggered: %s", str(e))
            personalization_model = None
            ai_available = False

        agent_meta = AgentMeta(
            actions_executed=actions_executed,
            personalization=personalization_model,
            ai_personalization_available=ai_available,
        )

        return AgentAnalyzeResponse(
            analysis=analysis_result,
            match=match_result,
            plan=plan_result,
            agent=agent_meta,
        )
