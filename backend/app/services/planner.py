import datetime
import re
from typing import List, Optional, Set, Tuple

from app.schemas import (
    ActionItem,
    ActionPlanResponse,
    GapItem,
    MatchResponse,
    PlanRequest,
    VerificationActionItem,
)
from app.services.matcher import parse_date_safely


def calculate_deadline_status(deadline_str: Optional[str]) -> Tuple[str, Optional[int]]:
    """
    Safely calculates the deadline status and remaining days relative to today.
    Never fabricates remaining days if the deadline cannot be reliably parsed.
    """
    if not deadline_str or not deadline_str.strip():
        return "No deadline specified.", None

    clean_deadline = deadline_str.strip()
    parsed_date = parse_date_safely(clean_deadline)

    if parsed_date is None:
        return "Deadline could not be reliably determined.", None

    today = datetime.date.today()
    days_remaining = (parsed_date - today).days

    if days_remaining > 1:
        return f"{days_remaining} days remaining ({clean_deadline})", days_remaining
    elif days_remaining == 1:
        return f"1 day remaining ({clean_deadline})", 1
    elif days_remaining == 0:
        return f"Deadline is today ({clean_deadline})", 0
    else:
        passed_days = abs(days_remaining)
        return f"Deadline has passed ({passed_days} days ago on {clean_deadline})", days_remaining


def get_canonical_action_key(category: str, requirement: str) -> str:
    """
    Maps category and requirement into a normalized semantic key
    to ensure semantically equivalent requirements produce only one action.
    """
    clean_cat = category.lower().strip()
    clean_req = requirement.lower().strip()

    # Citizenship / WNI
    if any(k in clean_req for k in ["wni", "warga negara", "indonesian citizen"]):
        return "eligibility:citizenship:wni"

    # Active student status
    if any(k in clean_req for k in ["mahasiswa aktif", "active university student", "active student"]):
        deg = re.search(r"\b(s1|d4|d3|s2)\b", clean_req)
        if deg:
            return f"eligibility:active_student:{deg.group(1)}"
        return "eligibility:active_student:general"

    # Scholarship restriction
    if any(k in clean_req for k in ["beasiswa", "scholarship"]) and any(k in clean_req for k in ["tidak sedang", "not currently", "other"]):
        return "eligibility:other_scholarships"

    # Open to all majors
    if any(k in clean_req for k in ["semua jurusan", "open to all majors"]):
        return "eligibility:open_all_majors"

    # CV / Resume
    if any(k in clean_req for k in ["cv", "curriculum vitae", "resume"]):
        return "document:cv_resume"

    # Transcript
    if any(k in clean_req for k in ["transkrip", "transcript"]):
        return "document:transcript"

    # Recommendation Letter
    if any(k in clean_req for k in ["rekomendasi", "recommendation"]):
        return "document:recommendation_letter"

    # Essay
    if any(k in clean_req for k in ["esai", "essay", "motivasi", "motivation"]):
        return "document:essay"

    # English Language Certificate
    if any(k in clean_req for k in ["toefl", "ielts", "kemampuan bahasa inggris", "english proficiency"]):
        return "document:english_cert"

    # GPA
    if "gpa" in clean_req or "ipk" in clean_req:
        return "academic:gpa"

    # Semester
    if "semester" in clean_req:
        return "academic:semester"

    norm_text = re.sub(r"[^a-z0-9]", "", clean_req)
    return f"{clean_cat}:{norm_text}"


def build_skill_action(skill_name: str) -> Tuple[str, str, str]:
    """
    Returns (action, reason, priority) for a missing skill.
    """
    clean_skill = skill_name.strip()
    skill_lower = clean_skill.lower()

    if "leadership" in skill_lower or "kepemimpinan" in skill_lower:
        return (
            "Tambahkan bukti pengalaman leadership yang relevan atau identifikasi pengalaman organisasi yang dapat menunjukkan kompetensi tersebut.",
            "Kemampuan leadership disyaratkan secara spesifik dalam kualifikasi kandidat.",
            "Medium",
        )
    elif "communication" in skill_lower or "komunikasi" in skill_lower:
        return (
            "Siapkan bukti pengalaman presentasi, teamwork, atau public speaking yang dapat mendukung kemampuan komunikasi.",
            "Kemampuan komunikasi merupakan kriteria utama penilaian dalam wawancara dan seleksi.",
            "Medium",
        )
    elif "python" in skill_lower:
        return (
            "Siapkan repositori proyek mini, portfolio GitHub, atau sertifikasi yang mendemonstrasikan keahlian Python.",
            "Keahlian teknis Python disyaratkan untuk penugasan dan kualifikasi teknis program.",
            "Medium",
        )
    elif "react" in skill_lower:
        return (
            "Siapkan portofolio aplikasi web berbasis React atau tautan demo proyek yang pernah dikerjakan.",
            "Keahlian frontend React merupakan salah satu kompetensi teknis yang dievaluasi.",
            "Medium",
        )
    elif "english" in skill_lower or "inggris" in skill_lower:
        return (
            "Siapkan sertifikat kemampuan bahasa Inggris atau dokumentasikan pengalaman komunikasi berbahasa Inggris.",
            "Kemampuan bahasa Inggris diperlukan untuk materi dan komunikasi program.",
            "Medium",
        )
    else:
        return (
            f"Perkuat profil dengan mencantumkan pengalaman proyek, sertifikasi, atau bukti portofolio terkait {clean_skill}.",
            f"Keahlian '{clean_skill}' tertera sebagai kualifikasi yang belum terdeteksi pada profil.",
            "Medium",
        )


def build_document_action(doc_name: str) -> Tuple[str, str, str]:
    """
    Returns (action, reason, priority) for a required document.
    """
    clean_doc = doc_name.strip()
    doc_lower = clean_doc.lower()

    if any(k in doc_lower for k in ["rekomendasi", "recommendation"]):
        return (
            "Hubungi dosen atau pembimbing akademik segera untuk meminta surat rekomendasi resmi.",
            "Memerlukan koordinasi dengan pihak eksternal/dosen yang membutuhkan waktu pemrosesan.",
            "High",
        )
    elif any(k in doc_lower for k in ["cv", "curriculum vitae", "resume"]):
        return (
            "Siapkan dan perbarui CV yang relevan dengan fokus opportunity ini.",
            "Dokumen utama untuk screening awal dan peninjauan profil kandidat.",
            "High",
        )
    elif any(k in doc_lower for k in ["transkrip", "transcript"]):
        return (
            "Siapkan transkrip nilai akademik terbaru yang telah dilegalisir dari program studi/fakultas.",
            "Dokumen resmi untuk verifikasi IPK dan status semester aktif.",
            "High",
        )
    elif any(k in doc_lower for k in ["esai", "essay", "motivasi", "motivation"]):
        return (
            "Susun draft esai sesuai tujuan dan kriteria program.",
            "Esai merupakan komponen krusial penilaian motivasi dan visi kandidat.",
            "High",
        )
    elif any(k in doc_lower for k in ["toefl", "ielts", "kemampuan bahasa inggris", "english proficiency"]):
        return (
            "Siapkan sertifikat kemampuan bahasa Inggris (TOEFL/IELTS) yang masih berlaku dengan skor yang memenuhi syarat.",
            "Sertifikat bahasa asing memerlukan waktu ujian atau verifikasi masa berlaku.",
            "High",
        )
    elif any(k in doc_lower for k in ["portofolio", "portfolio"]):
        return (
            "Kompilasi karya terbaik atau proyek relevan ke dalam dokumen portofolio terstruktur.",
            "Portofolio membuktikan kemampuan praktis secara langsung kepada tim penilai.",
            "High",
        )
    else:
        return (
            f"Siapkan dan verifikasi kelengkapan dokumen '{clean_doc}' sesuai ketentuan panitia.",
            "Dokumen wajib untuk kelengkapan administrasi pendaftaran.",
            "High",
        )


def build_verification_action(item_name: str) -> str:
    """
    Generates a constructive verification guidance action without treating it as a failure.
    """
    clean_item = item_name.strip()
    item_lower = clean_item.lower()

    if any(k in item_lower for k in ["wni", "warga negara", "indonesian citizen"]):
        return "Verifikasi bahwa persyaratan kewarganegaraan terpenuhi dan siapkan dokumen identitas (KTP/KK) jika diperlukan."
    elif any(k in item_lower for k in ["semua jurusan", "open to all majors"]):
        return "Konfirmasi bahwa program studi Anda termasuk dalam cakupan jurusan yang diperbolehkan oleh program."
    elif any(k in item_lower for k in ["mahasiswa aktif", "active university student", "active student"]):
        return "Siapkan surat keterangan mahasiswa aktif dari pihak kampus sebagai bukti registrasi semester."
    elif any(k in item_lower for k in ["beasiswa", "scholarship"]) and any(k in item_lower for k in ["tidak sedang", "not currently", "other"]):
        return "Pastikan Anda tidak sedang terikat beasiswa lain atau siapkan surat pernyataan bebas beasiswa."
    elif any(k in item_lower for k in ["cv", "resume", "transkrip", "transcript", "sertifikat", "dokumen"]):
        return f"Periksa apakah berkas '{clean_item}' sudah tersedia, masih berlaku, dan siap diunggah."
    else:
        return f"Periksa dan pastikan pemenuhan syarat '{clean_item}' sesuai pedoman resmi pendaftaran."


def generate_action_plan(request: PlanRequest) -> ActionPlanResponse:
    """
    Deterministic Action Planner service.
    Transforms match gaps, verified requirements, and deadline constraints
    into concrete, prioritized actions.
    """
    # 1. Resolve inputs
    match_result = request.match_result
    opportunity = request.opportunity

    gaps: List[GapItem] = (
        request.gaps
        if request.gaps is not None
        else (match_result.gaps if match_result else [])
    )
    needs_verification: List[GapItem] = (
        request.needs_verification
        if request.needs_verification is not None
        else (match_result.needs_verification if match_result else [])
    )
    matched: List[GapItem] = (
        request.matched
        if request.matched is not None
        else (match_result.matched if match_result else [])
    )

    raw_deadline = request.deadline
    if not raw_deadline and opportunity and opportunity.analysis:
        raw_deadline = opportunity.analysis.deadline

    # 2. Deadline awareness
    deadline_status, days_remaining = calculate_deadline_status(raw_deadline)
    is_urgent_deadline = days_remaining is not None and 0 <= days_remaining <= 7

    # 3. Generate Priority Actions
    priority_actions: List[ActionItem] = []
    seen_canonical_keys: Set[str] = set()

    # Track specific types for next best action selection
    recommendation_action: Optional[ActionItem] = None
    essay_action: Optional[ActionItem] = None
    doc_actions: List[ActionItem] = []
    eligibility_gap_actions: List[ActionItem] = []
    skill_gap_actions: List[ActionItem] = []

    # Process gaps
    for gap in gaps:
        canonical_key = get_canonical_action_key(gap.category, gap.requirement)
        if canonical_key in seen_canonical_keys:
            continue
        seen_canonical_keys.add(canonical_key)

        cat_lower = gap.category.lower()
        priority = "High" if is_urgent_deadline else "Medium"
        action_text = ""
        reason_text = ""

        if "skill" in cat_lower:
            action_text, reason_text, base_prio = build_skill_action(gap.requirement)
            priority = "High" if is_urgent_deadline else base_prio
            item = ActionItem(
                priority=priority,
                category="Skills",
                requirement=gap.requirement,
                action=action_text,
                reason=reason_text,
                status="todo",
            )
            priority_actions.append(item)
            skill_gap_actions.append(item)

        elif "document" in cat_lower:
            action_text, reason_text, base_prio = build_document_action(gap.requirement)
            item = ActionItem(
                priority="High",
                category="Documents",
                requirement=gap.requirement,
                action=action_text,
                reason=reason_text,
                status="todo",
            )
            priority_actions.append(item)
            doc_actions.append(item)
            if "rekomendasi" in gap.requirement.lower() or "recommendation" in gap.requirement.lower():
                recommendation_action = item
            elif "esai" in gap.requirement.lower() or "essay" in gap.requirement.lower():
                essay_action = item

        elif "academic" in cat_lower:
            if "gpa" in gap.requirement.lower() or "ipk" in gap.requirement.lower():
                action_text = "Pertimbangkan untuk meningkatkan IPK pada semester berjalan atau sertakan kompensasi prestasi akademik/sertifikasi unggulan."
                reason_text = "IPK saat ini berada di bawah batas minimum yang dipersyaratkan oleh program."
            else:
                action_text = "Pastikan linimasa pendaftaran sesuai dengan semester aktif atau periksa ketersediaan gelombang pendaftaran berikutnya."
                reason_text = "Semester aktif saat ini belum memenuhi rentang semester yang dipersyaratkan."
            item = ActionItem(
                priority="High",
                category="Academic",
                requirement=gap.requirement,
                action=action_text,
                reason=reason_text,
                status="todo",
            )
            priority_actions.append(item)
            eligibility_gap_actions.append(item)

        elif "eligibility" in cat_lower:
            action_text = f"Periksa apakah terdapat dispensasi jurusan atau konfirmasi relevansi kurikulum studi Anda untuk '{gap.requirement}'."
            reason_text = "Persyaratan kelayakan bersifat mutlak untuk seleksi administratif."
            item = ActionItem(
                priority="High",
                category="Eligibility",
                requirement=gap.requirement,
                action=action_text,
                reason=reason_text,
                status="todo",
            )
            priority_actions.append(item)
            eligibility_gap_actions.append(item)

        else:
            action_text = f"Tinjau dan penuhi ketentuan '{gap.requirement}' sebelum pendaftaran ditutup."
            reason_text = gap.message or "Kriteria wajib yang belum terpenuhi pada profil."
            item = ActionItem(
                priority="Medium",
                category="General",
                requirement=gap.requirement,
                action=action_text,
                reason=reason_text,
                status="todo",
            )
            priority_actions.append(item)

    # 4. Check for Document requirements in needs_verification that should be in priority_actions
    # (e.g. CV, Recommendation Letter, Transcript, Essay)
    verification_actions: List[VerificationActionItem] = []
    seen_verify_keys: Set[str] = set()

    for item in needs_verification:
        canonical_key = get_canonical_action_key(item.category, item.requirement)
        if canonical_key in seen_verify_keys:
            continue
        seen_verify_keys.add(canonical_key)

        req_lower = item.requirement.lower()

        # If it's a critical document that student MUST prepare, place in priority_actions if not already there
        is_critical_doc = item.category.lower() == "document" or any(
            k in req_lower for k in ["cv", "resume", "transkrip", "transcript", "rekomendasi", "recommendation", "esai", "essay", "toefl", "ielts"]
        )

        if is_critical_doc and canonical_key not in seen_canonical_keys:
            seen_canonical_keys.add(canonical_key)
            action_text, reason_text, base_prio = build_document_action(item.requirement)
            act_item = ActionItem(
                priority="High",
                category="Documents",
                requirement=item.requirement,
                action=action_text,
                reason=reason_text,
                status="todo",
            )
            priority_actions.append(act_item)
            doc_actions.append(act_item)
            if "rekomendasi" in req_lower or "recommendation" in req_lower:
                recommendation_action = act_item
            elif "esai" in req_lower or "essay" in req_lower:
                essay_action = act_item
        else:
            # Place in verification checklist
            guidance = build_verification_action(item.requirement)
            verification_actions.append(
                VerificationActionItem(
                    requirement=item.requirement,
                    action=guidance,
                    status="todo",
                )
            )

    # 5. Deterministic Next Best Action Selection
    # Hierarchy:
    # 1. External coordination (Recommendation letter)
    # 2. Eligibility blocker gap
    # 3. Core document preparation (Essay, then Transcript/CV)
    # 4. Skill gap
    # 5. Verification action
    # 6. Fallback
    next_best_action = ""
    if recommendation_action:
        next_best_action = "Hubungi dosen atau pembimbing untuk meminta surat rekomendasi terlebih dahulu, karena proses ini memerlukan koordinasi dengan pihak lain dan membutuhkan waktu."
    elif eligibility_gap_actions:
        next_best_action = f"Selesaikan konfirmasi syarat kelayakan '{eligibility_gap_actions[0].requirement}' terlebih dahulu sebelum menyiapkan berkas lainnya."
    elif essay_action:
        next_best_action = "Mulai susun draf esai atau surat motivasi sejak awal agar memiliki waktu untuk merevisi dan memoles argumen."
    elif doc_actions:
        next_best_action = f"Siapkan dokumen utama ({doc_actions[0].requirement}) agar seluruh berkas siap diunggah saat pendaftaran dibuka."
    elif skill_gap_actions:
        next_best_action = f"Fokuskan perhatian pada pemenuhan bukti kompetensi '{skill_gap_actions[0].requirement}' yang disyaratkan."
    elif verification_actions:
        next_best_action = f"Lakukan verifikasi administrasi untuk '{verification_actions[0].requirement}' guna memastikan kepatuhan berkas."
    else:
        next_best_action = "Periksa kembali kelengkapan seluruh berkas dan pantau jadwal pendaftaran resmi untuk submit tepat waktu."

    # 6. Summary generation
    total_gaps_count = len(priority_actions)
    verify_count = len(verification_actions)

    if total_gaps_count == 0 and verify_count == 0:
        summary = "Profil Anda telah memenuhi seluruh kriteria yang dievaluasi. Fokus utama Anda adalah memastikan dokumen pendaftaran diunggah sebelum batas waktu."
    elif total_gaps_count == 0 and verify_count > 0:
        summary = f"Profil Anda memiliki kesesuaian yang sangat baik tanpa gap kriteria utama, namun terdapat {verify_count} item yang memerlukan verifikasi administrasi sebelum pendaftaran."
    else:
        verify_phrase = f" dan {verify_count} persyaratan yang perlu diverifikasi" if verify_count > 0 else ""
        focus_phrase = (
            "Fokuskan langkah awal pada berkas yang memerlukan koordinasi pihak luar dan persiapan dokumen utama."
            if recommendation_action or doc_actions
            else "Fokuskan langkah awal pada pemenuhan gap kualifikasi utama."
        )
        summary = f"Anda memiliki profil yang potensial, namun terdapat {total_gaps_count} tindakan prioritas{verify_phrase}. {focus_phrase}"

    return ActionPlanResponse(
        summary=summary,
        priority_actions=priority_actions,
        verification_actions=verification_actions,
        deadline_status=deadline_status,
        next_best_action=next_best_action,
    )
