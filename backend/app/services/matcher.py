import datetime
import re
from typing import Any, Dict, List, Optional, Tuple

from app.schemas import (
    CategoryBreakdown,
    GapItem,
    MatchBreakdown,
    MatchResponse,
    OpportunityAnalyzeResponse,
    StudentProfile,
)
from app.services.analyzer import (
    is_pure_document_requirement,
    is_pure_gpa_requirement,
    is_pure_semester_requirement,
    is_pure_skill_requirement,
)

# Base Category Weights (Sum = 100)
WEIGHT_ELIGIBILITY = 40.0
WEIGHT_ACADEMIC = 20.0
WEIGHT_SKILLS = 15.0
WEIGHT_DOCUMENTS = 15.0
WEIGHT_DEADLINE = 10.0


def get_gap_item_key(item: GapItem) -> str:
    """
    Returns a normalized semantic key for a GapItem to prevent duplicate
    entries across matched, gaps, and needs_verification sections.
    """
    cat = item.category.lower().strip()
    req = item.requirement.lower().strip()

    # Academic GPA
    if "gpa" in req or "ipk" in req:
        return "academic:gpa"

    # Academic Semester
    if "semester" in req:
        return "academic:semester"

    # Citizenship / WNI
    if any(k in req for k in ["wni", "warga negara", "indonesian citizen"]):
        return "eligibility:citizenship:wni"

    # Active student status
    if any(k in req for k in ["mahasiswa aktif", "active university student", "active student"]):
        deg = re.search(r"\b(s1|d4|d3|s2)\b", req)
        if deg:
            return f"eligibility:active_student:{deg.group(1)}"
        return "eligibility:active_student:general"

    # Scholarship restriction
    if any(k in req for k in ["beasiswa", "scholarship"]) and any(k in req for k in ["tidak sedang", "not currently", "other"]):
        return "eligibility:other_scholarships"

    # Open to all majors
    if any(k in req for k in ["semua jurusan", "open to all majors"]):
        return "eligibility:open_all_majors"

    return f"{cat}:{req}"

MONTH_MAPPING = {
    # Indonesian
    "januari": 1, "jan": 1,
    "februari": 2, "feb": 2,
    "maret": 3, "mar": 3,
    "april": 4, "apr": 4,
    "mei": 5, "may": 5,
    "juni": 6, "jun": 6,
    "juli": 7, "jul": 7,
    "agustus": 8, "agu": 8, "aug": 8,
    "september": 9, "sep": 9,
    "oktober": 10, "okt": 10, "oct": 10,
    "november": 11, "nov": 11,
    "desember": 12, "des": 12, "dec": 12,
    # English
    "january": 1,
    "february": 2,
    "march": 3,
    "june": 6,
    "july": 7,
    "august": 8,
    "december": 12,
}


def parse_date_safely(date_str: str) -> Optional[datetime.date]:
    """
    Attempts to safely parse date string in Indonesian or English formats.
    Returns datetime.date if parsed, else None.
    """
    if not date_str:
        return None

    clean = date_str.strip()

    # Format 1: 15 Oktober 2026 or 15 Oct 2025
    m1 = re.search(r"\b([0-9]{1,2})\s+([A-Za-z]+)(?:\s+([0-9]{4}))?\b", clean)
    if m1:
        day = int(m1.group(1))
        month_name = m1.group(2).lower()
        year = int(m1.group(3)) if m1.group(3) else datetime.date.today().year
        month = MONTH_MAPPING.get(month_name)
        if month and 1 <= day <= 31:
            try:
                return datetime.date(year, month, day)
            except ValueError:
                pass

    # Format 2: October 15, 2025 or Dec 1 2025
    m2 = re.search(r"\b([A-Za-z]+)\s+([0-9]{1,2})(?:st|nd|rd|th)?,?\s+([0-9]{4})\b", clean)
    if m2:
        month_name = m2.group(1).lower()
        day = int(m2.group(2))
        year = int(m2.group(3))
        month = MONTH_MAPPING.get(month_name)
        if month and 1 <= day <= 31:
            try:
                return datetime.date(year, month, day)
            except ValueError:
                pass

    # Format 3: YYYY-MM-DD
    m3 = re.search(r"\b([0-9]{4})[-/]([0-9]{1,2})[-/]([0-9]{1,2})\b", clean)
    if m3:
        year = int(m3.group(1))
        month = int(m3.group(2))
        day = int(m3.group(3))
        if 1 <= month <= 12 and 1 <= day <= 31:
            try:
                return datetime.date(year, month, day)
            except ValueError:
                pass

    # Format 4: DD/MM/YYYY or DD-MM-YYYY
    m4 = re.search(r"\b([0-9]{1,2})[-/]([0-9]{1,2})[-/]([0-9]{4})\b", clean)
    if m4:
        day = int(m4.group(1))
        month = int(m4.group(2))
        year = int(m4.group(3))
        if 1 <= month <= 12 and 1 <= day <= 31:
            try:
                return datetime.date(year, month, day)
            except ValueError:
                pass

    return None


def evaluate_semester_requirement(
    student_semester: Optional[int],
    requirement_str: str
) -> Tuple[Optional[bool], str]:
    """
    Evaluates whether student's semester satisfies opportunity semester requirement.
    Returns (is_satisfied, explanation_message).
    """
    if student_semester is None:
        return (None, f"Semester requirement ({requirement_str}) specified, but your semester was not provided.")

    clean_req = requirement_str.lower().strip()

    # Range: e.g. "semester 5 - 7"
    range_match = re.search(r"semester\s*([0-9]+)\s*(?:-|–|sampai|to)\s*([0-9]+)", clean_req)
    if range_match:
        min_s = int(range_match.group(1))
        max_s = int(range_match.group(2))
        if min_s <= student_semester <= max_s:
            return (True, f"Your semester ({student_semester}) is within the eligible range ({requirement_str}).")
        else:
            return (False, f"Your current semester ({student_semester}) is outside the required range of Semester {min_s} - {max_s}.")

    # Plus / Minimal: e.g. "minimal semester 5", "semester 5+", "semester 3 ke atas"
    min_match = re.search(r"(?:minimal|minimum|min\.?)\s*semester\s*([0-9]+)|semester\s*([0-9]+)\s*(?:\+|ke\s*atas|dan\s+keatas)", clean_req)
    if min_match:
        min_s = int(min_match.group(1) or min_match.group(2))
        if student_semester >= min_s:
            return (True, f"Your semester ({student_semester}) meets the minimum requirement ({requirement_str}).")
        else:
            return (False, f"Your current semester ({student_semester}) is below the minimum requirement of Semester {min_s}.")

    # Single number e.g. "Semester 5"
    single_match = re.search(r"semester\s*([0-9]+)", clean_req)
    if single_match:
        target_s = int(single_match.group(1))
        if student_semester >= target_s:
            return (True, f"Your semester ({student_semester}) meets the requirement ({requirement_str}).")
        else:
            return (False, f"Your current semester ({student_semester}) does not meet the requirement of Semester {target_s}.")

    return (None, f"Unable to automatically verify semester requirement ({requirement_str}).")


def evaluate_gpa_requirement(
    student_gpa: Optional[float],
    min_gpa_str: str
) -> Tuple[Optional[bool], str]:
    """
    Evaluates whether student's GPA satisfies minimum GPA requirement.
    Returns (is_satisfied, explanation_message).
    """
    if student_gpa is None:
        return (None, f"Opportunity requires minimum GPA of {min_gpa_str}, but GPA was not provided in profile.")

    try:
        min_gpa = float(min_gpa_str.replace(",", ".").strip())
    except ValueError:
        return (None, f"Could not parse minimum GPA value '{min_gpa_str}'.")

    if student_gpa >= min_gpa:
        return (True, f"Your GPA ({student_gpa:.2f}) meets or exceeds the minimum GPA requirement ({min_gpa:.2f}).")
    else:
        return (False, f"Your GPA ({student_gpa:.2f}) is below the required minimum GPA of {min_gpa:.2f}.")


def evaluate_skills(
    student_skills: List[str],
    required_skills: List[str],
    experience: str = ""
) -> Tuple[List[str], List[str]]:
    """
    Compares normalized student skills and experience against required skills.
    Returns (matched_skills, missing_skills).
    """
    normalized_student_skills = [s.strip().lower() for s in student_skills if s.strip()]
    exp_lower = experience.lower() if experience else ""

    matched: List[str] = []
    missing: List[str] = []

    for req in required_skills:
        req_norm = req.strip().lower()
        if not req_norm:
            continue

        is_match = False

        # 1. Exact or substring match in student's declared skills
        for s in normalized_student_skills:
            if req_norm == s or req_norm in s or s in req_norm:
                is_match = True
                break

        # 2. Match in experience & achievements text via word boundary
        if not is_match and exp_lower:
            pattern = rf"\b{re.escape(req_norm)}\b"
            if re.search(pattern, exp_lower):
                is_match = True

        if is_match:
            matched.append(req)
        else:
            missing.append(req)

    return matched, missing


def calculate_match(
    profile: StudentProfile,
    opportunity: OpportunityAnalyzeResponse
) -> MatchResponse:
    """
    Deterministic scoring model and gap analysis generator.
    Weights:
      Eligibility: 40%
      Academic Fit: 20%
      Skills Fit: 15%
      Document Readiness: 15%
      Deadline Readiness: 10%
    Calculates score under uncertainty:
      earned_evaluable_weight / total_evaluable_weight * 100
    """
    analysis = opportunity.analysis
    matched_items: List[GapItem] = []
    gap_items: List[GapItem] = []
    needs_verification_items: List[GapItem] = []

    total_evaluable_weight = 0.0
    earned_evaluable_weight = 0.0

    # ---------------------------------------------------------
    # 1. ACADEMIC FIT (Weight 20)
    # ---------------------------------------------------------
    academic_sub_scores: List[float] = []
    has_academic_reqs = False

    # A. Minimum GPA
    if analysis.minimum_gpa:
        has_academic_reqs = True
        gpa_sat, gpa_msg = evaluate_gpa_requirement(profile.gpa, analysis.minimum_gpa)
        if gpa_sat is True:
            academic_sub_scores.append(1.0)
            matched_items.append(GapItem(
                category="Academic",
                requirement=f"Minimum GPA {analysis.minimum_gpa}",
                status="Satisfied",
                message=gpa_msg,
            ))
        elif gpa_sat is False:
            academic_sub_scores.append(0.0)
            gap_items.append(GapItem(
                category="Academic",
                requirement=f"Minimum GPA {analysis.minimum_gpa}",
                status="Missing",
                message=gpa_msg,
            ))
        else:
            # Unverifiable (student did not enter GPA)
            needs_verification_items.append(GapItem(
                category="Academic",
                requirement=f"Minimum GPA {analysis.minimum_gpa}",
                status="Needs Verification",
                message=gpa_msg,
            ))

    # B. Semester Requirement
    if analysis.semester_requirement:
        has_academic_reqs = True
        sem_sat, sem_msg = evaluate_semester_requirement(profile.semester, analysis.semester_requirement)
        if sem_sat is True:
            academic_sub_scores.append(1.0)
            matched_items.append(GapItem(
                category="Academic",
                requirement=analysis.semester_requirement,
                status="Satisfied",
                message=sem_msg,
            ))
        elif sem_sat is False:
            academic_sub_scores.append(0.0)
            gap_items.append(GapItem(
                category="Academic",
                requirement=analysis.semester_requirement,
                status="Missing",
                message=sem_msg,
            ))
        else:
            needs_verification_items.append(GapItem(
                category="Academic",
                requirement=analysis.semester_requirement,
                status="Needs Verification",
                message=sem_msg,
            ))

    # Calculate Academic Category Breakdown
    if not has_academic_reqs:
        academic_breakdown = CategoryBreakdown(
            weight=WEIGHT_ACADEMIC,
            status="not_specified",
            score=None,
            detail="No GPA or semester requirement was specified.",
        )
    elif academic_sub_scores:
        avg_score = sum(academic_sub_scores) / len(academic_sub_scores)
        cat_score = round(WEIGHT_ACADEMIC * avg_score, 1)
        total_evaluable_weight += WEIGHT_ACADEMIC
        earned_evaluable_weight += cat_score

        if avg_score == 1.0:
            status = "matched"
        elif avg_score > 0.0:
            status = "partial"
        else:
            status = "missing"

        academic_breakdown = CategoryBreakdown(
            weight=WEIGHT_ACADEMIC,
            status=status,
            score=cat_score,
            detail=f"{len([s for s in academic_sub_scores if s == 1.0])}/{len(academic_sub_scores)} academic criteria satisfied.",
        )
    else:
        # Academic requirements exist, but student profile lacked data to evaluate
        academic_breakdown = CategoryBreakdown(
            weight=WEIGHT_ACADEMIC,
            status="needs_verification",
            score=None,
            detail="Academic requirements were specified but profile data is missing.",
        )

    # ---------------------------------------------------------
    # 2. SKILLS FIT (Weight 15)
    # ---------------------------------------------------------
    required_skills = analysis.required_skills
    if not required_skills:
        skills_breakdown = CategoryBreakdown(
            weight=WEIGHT_SKILLS,
            status="not_specified",
            score=None,
            detail="No required skills were specified.",
        )
    else:
        matched_skills, missing_skills = evaluate_skills(
            student_skills=profile.skills,
            required_skills=required_skills,
            experience=profile.experience or "",
        )

        for s in matched_skills:
            matched_items.append(GapItem(
                category="Skill",
                requirement=s,
                status="Satisfied",
                message=f"'{s}' is present in your skills or experience.",
            ))

        for s in missing_skills:
            gap_items.append(GapItem(
                category="Skill",
                requirement=s,
                status="Missing",
                message=f"'{s}' is listed as a required skill but is not found in your profile.",
            ))

        ratio = len(matched_skills) / len(required_skills)
        cat_score = round(WEIGHT_SKILLS * ratio, 1)
        total_evaluable_weight += WEIGHT_SKILLS
        earned_evaluable_weight += cat_score

        if ratio == 1.0:
            status = "matched"
        elif ratio > 0.0:
            status = "partial"
        else:
            status = "missing"

        skills_breakdown = CategoryBreakdown(
            weight=WEIGHT_SKILLS,
            status=status,
            score=cat_score,
            detail=f"{len(matched_skills)} of {len(required_skills)} required skill(s) matched.",
        )

    # ---------------------------------------------------------
    # 3. ELIGIBILITY (Weight 40)
    # ---------------------------------------------------------
    eligibility_list = analysis.eligibility
    if not eligibility_list:
        eligibility_breakdown = CategoryBreakdown(
            weight=WEIGHT_ELIGIBILITY,
            status="not_specified",
            score=None,
            detail="No specific eligibility criteria specified.",
        )
    else:
        evaluable_eligibility_scores: List[float] = []

        for req in eligibility_list:
            req_clean = req.strip()
            req_lower = req_clean.lower()

            # Skip pure academic, skill, or document criteria that belong to other categories
            if (
                is_pure_gpa_requirement(req_clean)
                or is_pure_semester_requirement(req_clean)
                or is_pure_skill_requirement(req_clean)
                or is_pure_document_requirement(req_clean)
            ):
                continue

            # A. Open to all majors
            if re.search(r"\b(?:terbuka\s+untuk\s+semua\s+(?:jurusan|program\s+studi)|semua\s+jurusan|open\s+to\s+all\s+majors)\b", req_lower):
                evaluable_eligibility_scores.append(1.0)
                matched_items.append(GapItem(
                    category="Eligibility",
                    requirement=req_clean,
                    status="Satisfied",
                    message="Opportunity is open to all study programs and majors.",
                ))
            # B. Specific Study Program matching
            elif profile.study_program and re.search(r"\b(?:jurusan|program\s+studi|major)\b", req_lower):
                std_prog_lower = profile.study_program.lower()
                if any(w in req_lower for w in std_prog_lower.split() if len(w) > 3):
                    evaluable_eligibility_scores.append(1.0)
                    matched_items.append(GapItem(
                        category="Eligibility",
                        requirement=req_clean,
                        status="Satisfied",
                        message=f"Your study program ({profile.study_program}) matches the eligible majors.",
                    ))
                else:
                    evaluable_eligibility_scores.append(0.0)
                    gap_items.append(GapItem(
                        category="Eligibility",
                        requirement=req_clean,
                        status="Missing",
                        message=f"Your study program ({profile.study_program}) does not explicitly match: {req_clean}",
                    ))
            # C. Active student status
            elif re.search(r"\b(?:mahasiswa\s+aktif(?:\s+(?:s1|d4|d3|s2))?|active\s+(?:university\s+)?student)\b", req_lower):
                if any(m.category == "Eligibility" and any(k in m.requirement.lower() for k in ["mahasiswa aktif", "active university student", "active student"]) for m in matched_items):
                    continue
                if profile.semester is not None or profile.study_program:
                    evaluable_eligibility_scores.append(1.0)
                    matched_items.append(GapItem(
                        category="Eligibility",
                        requirement=req_clean,
                        status="Satisfied",
                        message=f"Active student enrollment verified ({profile.study_program or 'University Student'}, Semester {profile.semester or 'Active'}).",
                    ))
                else:
                    needs_verification_items.append(GapItem(
                        category="Eligibility",
                        requirement=req_clean,
                        status="Needs Verification",
                        message=f"Requires active student enrollment; profile lacks enrollment details.",
                    ))
            # D. Citizenship (WNI)
            elif re.search(r"\b(?:wni|warga\s+negara\s+indonesia|indonesian\s+citizen)\b", req_lower):
                if not any(v.category == "Eligibility" and any(k in v.requirement.lower() for k in ["wni", "warga", "indonesian citizen"]) for v in needs_verification_items):
                    needs_verification_items.append(GapItem(
                        category="Eligibility",
                        requirement="Indonesian Citizen (WNI)",
                        status="Needs Verification",
                        message="Requires verification of Indonesian citizenship (WNI).",
                    ))
            # E. Other non-evaluable eligibility criteria (e.g. no concurrent scholarships)
            else:
                needs_verification_items.append(GapItem(
                    category="Eligibility",
                    requirement=req_clean,
                    status="Needs Verification",
                    message=f"'{req_clean}' requires external documentation / manual verification.",
                ))

        if evaluable_eligibility_scores:
            ratio = sum(evaluable_eligibility_scores) / len(evaluable_eligibility_scores)
            cat_score = round(WEIGHT_ELIGIBILITY * ratio, 1)
            total_evaluable_weight += WEIGHT_ELIGIBILITY
            earned_evaluable_weight += cat_score

            if ratio == 1.0:
                status = "matched"
            elif ratio > 0.0:
                status = "partial"
            else:
                status = "missing"

            eligibility_breakdown = CategoryBreakdown(
                weight=WEIGHT_ELIGIBILITY,
                status=status,
                score=cat_score,
                detail=f"{len([s for s in evaluable_eligibility_scores if s == 1.0])}/{len(evaluable_eligibility_scores)} evaluable eligibility criteria verified.",
            )
        else:
            eligibility_breakdown = CategoryBreakdown(
                weight=WEIGHT_ELIGIBILITY,
                status="needs_verification",
                score=None,
                detail="Eligibility criteria require manual verification (e.g., citizenship or external status).",
            )

    # ---------------------------------------------------------
    # 4. DOCUMENT READINESS (Weight 15)
    # ---------------------------------------------------------
    # Current profile does not yet collect uploaded documents.
    # Therefore, documents are marked as needs_verification and not penalized.
    required_docs = analysis.required_documents
    if not required_docs:
        documents_breakdown = CategoryBreakdown(
            weight=WEIGHT_DOCUMENTS,
            status="not_specified",
            score=None,
            detail="No required documents were specified.",
        )
    else:
        for doc in required_docs:
            needs_verification_items.append(GapItem(
                category="Document",
                requirement=doc,
                status="Needs Verification",
                message=f"'{doc}' is required and must be prepared before submission.",
            ))

        documents_breakdown = CategoryBreakdown(
            weight=WEIGHT_DOCUMENTS,
            status="needs_verification",
            score=None,
            detail=f"{len(required_docs)} required document(s) listed for preparation.",
        )

    # ---------------------------------------------------------
    # 5. DEADLINE READINESS (Weight 10)
    # ---------------------------------------------------------
    deadline_str = analysis.deadline
    if not deadline_str:
        deadline_breakdown = CategoryBreakdown(
            weight=WEIGHT_DEADLINE,
            status="not_specified",
            score=None,
            detail="No application deadline was specified.",
        )
    else:
        parsed_date = parse_date_safely(deadline_str)
        if parsed_date:
            today = datetime.date.today()
            if parsed_date > today:
                status = "upcoming"
                cat_score = WEIGHT_DEADLINE
                total_evaluable_weight += WEIGHT_DEADLINE
                earned_evaluable_weight += cat_score
                matched_items.append(GapItem(
                    category="Deadline",
                    requirement=f"Deadline: {deadline_str}",
                    status="Satisfied",
                    message=f"Application deadline is upcoming ({deadline_str}).",
                ))
            elif parsed_date == today:
                status = "today"
                cat_score = WEIGHT_DEADLINE
                total_evaluable_weight += WEIGHT_DEADLINE
                earned_evaluable_weight += cat_score
                matched_items.append(GapItem(
                    category="Deadline",
                    requirement=f"Deadline: {deadline_str}",
                    status="Satisfied",
                    message=f"Application deadline is today ({deadline_str}).",
                ))
            else:
                status = "passed"
                cat_score = 0.0
                total_evaluable_weight += WEIGHT_DEADLINE
                earned_evaluable_weight += cat_score
                gap_items.append(GapItem(
                    category="Deadline",
                    requirement=f"Deadline: {deadline_str}",
                    status="Missing",
                    message=f"Application deadline ({deadline_str}) has already passed.",
                ))

            deadline_breakdown = CategoryBreakdown(
                weight=WEIGHT_DEADLINE,
                status=status,
                score=cat_score,
                detail=f"Deadline is {status} ({deadline_str}).",
            )
        else:
            needs_verification_items.append(GapItem(
                category="Deadline",
                requirement="Application Deadline",
                status="Needs Verification",
                message=f"Deadline date '{deadline_str}' could not be parsed safely; verify date manually.",
            ))
            deadline_breakdown = CategoryBreakdown(
                weight=WEIGHT_DEADLINE,
                status="unknown",
                score=None,
                detail=f"Deadline format requires manual verification ({deadline_str}).",
            )

    # ---------------------------------------------------------
    # FINAL SCORE CALCULATION (Scoring Under Uncertainty)
    # ---------------------------------------------------------
    if total_evaluable_weight > 0:
        match_score = int(round((earned_evaluable_weight / total_evaluable_weight) * 100))
    else:
        # If no requirements were evaluable at all, baseline readiness is neutral/high
        match_score = 100

    match_score = max(0, min(100, match_score))

    # ---------------------------------------------------------
    # DEFENSIVE DEDUPLICATION (Gap Analysis & Verification Items)
    # ---------------------------------------------------------
    evaluated_keys = set()
    for item in matched_items + gap_items:
        key = get_gap_item_key(item)
        evaluated_keys.add(key)

    clean_needs_verification: List[GapItem] = []
    seen_verify_keys = set()

    for item in needs_verification_items:
        key = get_gap_item_key(item)
        # Exclude if already satisfied or identified as gap in primary categories
        if key in evaluated_keys:
            continue
        # Exclude duplicate keys within needs_verification
        if key in seen_verify_keys:
            continue
        seen_verify_keys.add(key)
        clean_needs_verification.append(item)

    needs_verification_items = clean_needs_verification

    # Summary text generation
    summary = generate_summary(
        score=match_score,
        gaps=gap_items,
        needs_verification=needs_verification_items,
    )

    return MatchResponse(
        match_score=match_score,
        summary=summary,
        breakdown=MatchBreakdown(
            eligibility=eligibility_breakdown,
            academic=academic_breakdown,
            skills=skills_breakdown,
            documents=documents_breakdown,
            deadline=deadline_breakdown,
        ),
        matched=matched_items,
        gaps=gap_items,
        needs_verification=needs_verification_items,
    )


def generate_summary(
    score: int,
    gaps: List[GapItem],
    needs_verification: List[GapItem]
) -> str:
    """
    Generates a clear human-readable summary reflecting profile alignment.
    Never refers to acceptance probability.
    """
    missing_skills = [g.requirement for g in gaps if g.category == "Skill"]
    academic_gaps = [g for g in gaps if g.category == "Academic"]

    if score >= 80:
        if missing_skills:
            return f"Strong alignment with the opportunity requirements, with {len(missing_skills)} skill(s) still needing attention."
        elif needs_verification:
            return "Strong profile match on evaluated criteria. Ensure required documents and external eligibility are verified."
        else:
            return "Excellent profile match across all evaluated requirements."
    elif score >= 60:
        if academic_gaps and missing_skills:
            return "Moderate profile match. Academic criteria and key skills need attention to improve alignment."
        elif missing_skills:
            return f"Good potential match, with {len(missing_skills)} required skill(s) still missing from your profile."
        else:
            return "Moderate match. Several core requirements are met, while some criteria require attention or verification."
    elif score >= 40:
        return "Partial alignment with the opportunity. Several key requirements or skills are currently missing from your profile."
    else:
        return "Low alignment based on the provided profile. Core academic or skill requirements are not currently met."
