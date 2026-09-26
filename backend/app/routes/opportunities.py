from fastapi import APIRouter, HTTPException, status
from app.schemas import (
    MatchRequest,
    MatchResponse,
    OpportunityAnalyzeRequest,
    OpportunityAnalyzeResponse,
)
from app.services.analyzer import analyze_opportunity
from app.services.matcher import calculate_match

router = APIRouter()


@router.post(
    "/analyze",
    response_model=OpportunityAnalyzeResponse,
    summary="Analyze Opportunity Description",
    description="Deterministically extracts requirements, deadlines, GPA, skills, documents, and benefits from an opportunity description.",
)
def analyze(payload: OpportunityAnalyzeRequest):
    if not payload.opportunity_type or not payload.opportunity_type.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="opportunity_type is required and cannot be empty.",
        )
    if not payload.description or not payload.description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="description is required and cannot be empty or only whitespace.",
        )

    result = analyze_opportunity(
        opportunity_type=payload.opportunity_type.strip(),
        description=payload.description.strip(),
    )
    return result


@router.post(
    "/match",
    response_model=MatchResponse,
    summary="Match Student Profile with Opportunity",
    description="Evaluates profile match against structured opportunity analysis and generates a detailed gap analysis.",
)
def match(payload: MatchRequest):
    return calculate_match(
        profile=payload.profile,
        opportunity=payload.opportunity,
    )
