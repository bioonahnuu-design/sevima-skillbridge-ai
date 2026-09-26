import re
from typing import Any, Dict, List, Optional


# ============================================================
# DOCUMENT GROUNDING CONFIGURATION
# ============================================================

# Canonical document categories and the phrases that identify them.
#
# IMPORTANT:
# Generic "sertifikat" / "certificate" MUST NOT be matched by itself.
# Otherwise phrases such as:
#
#   "sertifikat penyelesaian"
#   "mendapat sertifikat"
#   "certificate of completion"
#
# could incorrectly be interpreted as application requirements.
#
# Only explicit document categories are included here.
DOCUMENT_CATEGORY_PATTERNS: Dict[str, List[str]] = {
    "Curriculum Vitae (CV) / Resume": [
        r"\bcv\b",
        r"\bcurriculum\s+vitae\b",
        r"\bresume\b",
    ],

    "Academic Transcript": [
        r"\btranskrip(?:\s+nilai)?\b",
        r"\bacademic\s+transcript\b",
        r"\btranscript\b",
    ],

    "Recommendation Letter": [
        r"\bsurat\s+rekomendasi\b",
        r"\brecommendation\s+letter\b",
        r"\bletter\s+of\s+recommendation\b",
    ],

    "Motivation Letter / Statement of Purpose": [
        r"\bsurat\s+motivasi\b",
        r"\bmotivation\s+letter\b",
        r"\bstatement\s+of\s+purpose\b",
        r"\bsop\b",
    ],

    "Essay": [
        r"\besai\b",
        r"\bessay\b",
    ],

    "Portfolio": [
        r"\bportofolio\b",
        r"\bportfolio\b",
    ],

    # IMPORTANT:
    # Do NOT add a generic:
    #
    #   r"\bsertifikat\b"
    #
    # here.
    #
    # Certificates must be explicit achievement/evidence certificates.
    "Certificates / Awards": [
        r"\bsertifikat\s+prestasi\b",
        r"\bsertifikat\s+penghargaan\b",
        r"\bsertifikat\s+kejuaraan\b",
        r"\bsertifikat\s+lomba\b",
        r"\bsertifikat\s+akademik\b",
        r"\bsertifikat\s+kompetensi\b",
        r"\bsertifikat\s+keahlian\b",
        r"\bsertifikat\s+organisasi\b",
        r"\bsertifikat\s+seminar\b",
        r"\bsertifikat\s+pelatihan\b",
        r"\bcertificate\s+of\s+achievement\b",
        r"\bcertificate\s+of\s+merit\b",
        r"\bcertificate\s+of\s+excellence\b",
        r"\bachievement\s+certificate\b",
        r"\baward\s+certificate\b",
    ],

    "English Proficiency Certificate (TOEFL/IELTS)": [
        r"\btoefl\b",
        r"\bielts\b",
        r"\btoeic\b",
        r"\bduolingo\s+english\s+test\b",
        r"\bsertifikat\s+(?:kemampuan\s+)?bahasa(?:\s+inggris)?\b",
        r"\benglish\s+proficiency\s+certificate\b",
    ],

    "Certificate of Active Enrollment": [
        r"\bsurat\s+keterangan\s+aktif\s+kuliah\b",
        r"\bcertificate\s+of\s+active\s+enrollment\b",
    ],

    "Study Plan / Proposal": [
        r"\brancangan\s+studi\b",
        r"\bstudy\s+plan\b",
        r"\brencana\s+studi\b",
    ],

    "Financial Statement / Salary Slip": [
        r"\bsurat\s+keterangan\s+penghasilan\b",
        r"\bslip\s+gaji\b",
        r"\bfinancial\s+statement\b",
        r"\bsalary\s+slip\b",
    ],

    "SKCK": [
        r"\bskck\b",
    ],

    "Passport Photo": [
        r"\bpas\s*foto\b",
        r"\bpassport\s+photo\b",
        r"\bfoto\s+(?:terbaru|3x4|4x6)\b",
    ],

    "Student ID (KTM)": [
        r"\bktm\b",
        r"\bkartu\s+tanda\s+mahasiswa\b",
        r"\bstudent\s+id\b",
    ],

    "ID Card (KTP)": [
        r"\bktp\b",
        r"\bkartu\s+tanda\s+penduduk\b",
        r"\bid\s+card\b",
        r"\bidentitas\s+diri\b",
    ],
}


# Generic phrases that imply application documents even when a specific
# document type is not named.
#
# These are considered unsupported when deterministic analysis says that
# no documents are required.
GENERIC_DOCUMENT_PATTERNS: List[str] = [
    r"\bberkas\s+(?:pendaftaran|lamaran|persyaratan|administrasi)\b",
    r"\bdokumen\s+(?:pendaftaran|lamaran|persyaratan|administrasi|pendukung)\b",
    r"\bapplication\s+documents?\b",
    r"\bsupporting\s+documents?\b",
]


# ============================================================
# AUTHORIZATION / GROUNDING HELPERS
# ============================================================

def _normalize_document_name(value: str) -> str:
    """
    Normalizes deterministic document names for comparison.
    """
    return re.sub(r"\s+", " ", str(value).strip().lower())


def _is_category_authorized(
    category_name: str,
    required_documents: List[str],
) -> bool:
    """
    Returns True when a canonical document category is supported by
    deterministic required_documents.

    Exact canonical matches are preferred, while limited containment
    support is retained for compatible deterministic labels.
    """
    category = _normalize_document_name(category_name)

    for required in required_documents:
        req = _normalize_document_name(required)

        if not req:
            continue

        if req == category:
            return True

        if req in category or category in req:
            return True

    return False


def build_unauthorized_document_regex(
    required_documents: List[str],
) -> Optional[re.Pattern]:
    """
    Builds one regex containing document mentions that AI is NOT allowed
    to introduce.

    Behavior:

    1. required_documents == []
       -> every explicit application-document category is unauthorized
       -> generic application-document instructions are unauthorized

    2. required_documents contains specific documents
       -> those categories are authorized
       -> all other document categories remain unauthorized

    This lets legitimate document guidance survive while blocking
    hallucinated requirements.
    """
    required_documents = required_documents or []

    unauthorized_patterns: List[str] = []

    # No deterministic document requirements means AI should not invent
    # generic "prepare application documents" guidance either.
    if not required_documents:
        unauthorized_patterns.extend(GENERIC_DOCUMENT_PATTERNS)

    for category_name, patterns in DOCUMENT_CATEGORY_PATTERNS.items():
        if not _is_category_authorized(
            category_name,
            required_documents,
        ):
            unauthorized_patterns.extend(patterns)

    if not unauthorized_patterns:
        return None

    combined_pattern = "|".join(
        f"(?:{pattern})"
        for pattern in unauthorized_patterns
    )

    return re.compile(
        combined_pattern,
        re.IGNORECASE,
    )


def contains_unsupported_document_mention(
    text: str,
    unauthorized_regex: Optional[re.Pattern],
) -> bool:
    """
    Returns True when AI-generated text contains an application-document
    reference that is not supported by deterministic analysis.
    """
    if not text:
        return False

    if unauthorized_regex is None:
        return False

    return bool(
        unauthorized_regex.search(str(text))
    )


# ============================================================
# TEXT SANITIZATION
# ============================================================

def sanitize_text_field(
    text: str,
    unauthorized_regex: Optional[re.Pattern],
    fallback: str,
) -> str:
    """
    Removes sentences containing unsupported document recommendations.

    Example:

        "Your profile is strong. Prepare your CV."

    with CV unauthorized becomes:

        "Your profile is strong."

    If every sentence is removed, a deterministic-safe fallback is used.
    """
    if not text or not str(text).strip():
        return fallback

    text = str(text).strip()

    if unauthorized_regex is None:
        return text

    # Split prose into sentences.
    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    clean_sentences: List[str] = []

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        if contains_unsupported_document_mention(
            sentence,
            unauthorized_regex,
        ):
            continue

        clean_sentences.append(sentence)

    cleaned = " ".join(clean_sentences).strip()

    return cleaned if cleaned else fallback


def sanitize_focus_areas(
    focus_areas: Any,
    unauthorized_regex: Optional[re.Pattern],
    grounded_context: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """
    Sanitizes AI-generated focus areas.

    Unsupported document recommendations are removed individually while
    valid non-document guidance is preserved.

    Example:

        [
            "Siapkan CV dan transkrip nilai",
            "Pelajari React testing"
        ]

    becomes:

        [
            "Pelajari React testing"
        ]

    when CV/transcript are not deterministic requirements.
    """
    if isinstance(focus_areas, str):
        candidates = [focus_areas]

    elif isinstance(focus_areas, list):
        candidates = [
            str(item)
            for item in focus_areas
            if item is not None and str(item).strip()
        ]

    else:
        candidates = []

    clean_focus: List[str] = []

    for item in candidates:
        item = item.strip()

        if not item:
            continue

        if contains_unsupported_document_mention(
            item,
            unauthorized_regex,
        ):
            continue

        clean_focus.append(item)

    # If valid focus areas remain, preserve them.
    if clean_focus:
        return clean_focus

    # Otherwise derive a safe fallback from deterministic context.
    if grounded_context:
        profile_match = grounded_context.get(
            "profile_match_results",
            {},
        )

        gaps = profile_match.get(
            "requirement_gaps",
            [],
        )

        if isinstance(gaps, list) and gaps:
            first_gap = gaps[0]

            if isinstance(first_gap, dict):
                requirement = (
                    first_gap.get("requirement")
                    or first_gap.get("name")
                    or first_gap.get("category")
                )

                if requirement:
                    return [
                        f"Fokus meningkatkan kesiapan pada {requirement}"
                    ]

    return [
        "Lanjutkan persiapan terarah sesuai kriteria program."
    ]


# ============================================================
# MAIN PERSONALIZATION GROUNDING VALIDATOR
# ============================================================

def validate_and_sanitize_personalization(
    raw_ai: Dict[str, Any],
    required_documents: List[str],
    grounded_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Final defensive grounding layer for AI personalization.

    Deterministic analysis remains the source of truth.

    The AI provider is allowed to:
    - explain results
    - summarize results
    - prioritize grounded gaps
    - personalize guidance

    The AI provider is NOT allowed to invent application-document
    requirements absent from deterministic analysis.

    The validator runs AFTER the AI provider returns its output so that
    even a rogue/malformed provider cannot bypass grounding.
    """
    if not raw_ai or not isinstance(raw_ai, dict):
        return raw_ai

    required_documents = required_documents or []

    unauthorized_regex = build_unauthorized_document_regex(
        required_documents
    )

    sanitized: Dict[str, Any] = dict(raw_ai)

    # --------------------------------------------------------
    # 1. FOCUS AREAS
    # --------------------------------------------------------

    if "focus_areas" in sanitized:
        sanitized["focus_areas"] = sanitize_focus_areas(
            sanitized.get("focus_areas"),
            unauthorized_regex,
            grounded_context,
        )

    # --------------------------------------------------------
    # 2. RECOMMENDED STRATEGY
    # --------------------------------------------------------

    if isinstance(
        sanitized.get("recommended_strategy"),
        str,
    ):
        sanitized["recommended_strategy"] = sanitize_text_field(
            sanitized["recommended_strategy"],
            unauthorized_regex,
            fallback=(
                "Fokus pada pemenuhan kriteria akademik dan "
                "keahlian yang disyaratkan program ini."
            ),
        )

    # --------------------------------------------------------
    # 3. SUMMARY
    # --------------------------------------------------------

    if isinstance(
        sanitized.get("summary"),
        str,
    ):
        sanitized["summary"] = sanitize_text_field(
            sanitized["summary"],
            unauthorized_regex,
            fallback=(
                "Profil Anda telah dievaluasi berdasarkan "
                "kriteria terverifikasi untuk program ini."
            ),
        )

    # --------------------------------------------------------
    # 4. WHY THIS MATCH
    # --------------------------------------------------------

    if isinstance(
        sanitized.get("why_this_match"),
        str,
    ):
        sanitized["why_this_match"] = sanitize_text_field(
            sanitized["why_this_match"],
            unauthorized_regex,
            fallback=(
                "Kualifikasi Anda dinilai langsung terhadap "
                "prasyarat program yang teridentifikasi."
            ),
        )

    # --------------------------------------------------------
    # 5. ENCOURAGEMENT
    # --------------------------------------------------------

    if isinstance(
        sanitized.get("encouragement"),
        str,
    ):
        sanitized["encouragement"] = sanitize_text_field(
            sanitized["encouragement"],
            unauthorized_regex,
            fallback=(
                "Tetap konsisten mempersiapkan kriteria yang "
                "memang dibutuhkan program."
            ),
        )

    return sanitized