from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class OpportunityAnalyzeRequest(BaseModel):
    opportunity_type: str = Field(..., description="Opportunity type, e.g. Scholarship, Internship")
    description: str = Field(..., description="Full text description of the opportunity")

    @field_validator("opportunity_type")
    @classmethod
    def validate_opportunity_type(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("opportunity_type is required and cannot be empty.")
        return value.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("description is required and cannot be empty or only whitespace.")
        return value.strip()


class OpportunityAnalysisData(BaseModel):
    deadline: Optional[str] = None
    minimum_gpa: Optional[str] = None
    semester_requirement: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    eligibility: List[str] = Field(default_factory=list)


class OpportunityAnalyzeResponse(BaseModel):
    opportunity_type: str
    analysis: OpportunityAnalysisData


class StudentProfile(BaseModel):
    study_program: Optional[str] = Field(default="", description="Student's study program or major")
    semester: Optional[int] = Field(default=None, description="Student's current semester")
    gpa: Optional[float] = Field(default=None, description="Student's current cumulative GPA")
    skills: List[str] = Field(default_factory=list, description="Student's skills list")
    experience: Optional[str] = Field(default="", description="Student's experience and achievements")


class MatchRequest(BaseModel):
    profile: StudentProfile
    opportunity: OpportunityAnalyzeResponse


class CategoryBreakdown(BaseModel):
    weight: float
    status: str  # "matched", "partial", "missing", "needs_verification", "not_specified", "upcoming", "passed"
    score: Optional[float] = None
    detail: Optional[str] = None


class MatchBreakdown(BaseModel):
    eligibility: CategoryBreakdown
    academic: CategoryBreakdown
    skills: CategoryBreakdown
    documents: CategoryBreakdown
    deadline: CategoryBreakdown


class GapItem(BaseModel):
    category: str
    requirement: str
    status: str  # "Satisfied", "Missing", "Needs Verification"
    message: str


class MatchResponse(BaseModel):
    match_score: int
    summary: str
    breakdown: MatchBreakdown
    matched: List[GapItem] = Field(default_factory=list)
    gaps: List[GapItem] = Field(default_factory=list)
    needs_verification: List[GapItem] = Field(default_factory=list)


class ActionItem(BaseModel):
    priority: str = Field(..., description="Priority level: High, Medium, or Low")
    category: str = Field(..., description="Category, e.g. Skills, Documents, Academic, Eligibility")
    requirement: str = Field(..., description="The requirement or gap being addressed")
    action: str = Field(..., description="Concrete action recommendation")
    reason: str = Field(..., description="Rationale for the action and priority")
    status: str = Field(default="todo", description="Task completion status")


class VerificationActionItem(BaseModel):
    requirement: str = Field(..., description="Requirement to be verified")
    action: str = Field(..., description="Verification guidance step")
    status: str = Field(default="todo", description="Verification status")


class ActionPlanResponse(BaseModel):
    summary: str = Field(..., description="Overall action plan summary")
    priority_actions: List[ActionItem] = Field(default_factory=list, description="Prioritized list of actionable steps")
    verification_actions: List[VerificationActionItem] = Field(default_factory=list, description="List of verification steps")
    deadline_status: str = Field(..., description="Deadline status and remaining time analysis")
    next_best_action: str = Field(..., description="The single highest-leverage immediate action to take")


class PlanRequest(BaseModel):
    match_result: Optional[MatchResponse] = None
    opportunity: Optional[OpportunityAnalyzeResponse] = None
    gaps: Optional[List[GapItem]] = None
    needs_verification: Optional[List[GapItem]] = None
    matched: Optional[List[GapItem]] = None
    deadline: Optional[str] = None

