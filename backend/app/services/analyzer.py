import re
from typing import Any, Dict, List, Optional


# Canonical Skills Dictionary with regex patterns
SKILL_PATTERNS = [
    # Programming & Tech
    (r"\bpython\b", "Python"),
    (r"\bjavascript\b|\bjs\b", "JavaScript"),
    (r"\btypescript\b|\bts\b", "TypeScript"),
    (r"\breact(?:\.js)?\b", "React"),
    (r"\bvue(?:\.js)?\b", "Vue.js"),
    (r"\bangular\b", "Angular"),
    (r"\bnode(?:\.js)?\b", "Node.js"),
    (r"\bjava\b(?!\s*script)", "Java"),
    (r"\bc\+\+\b", "C++"),
    (r"\bc#\b", "C#"),
    (r"\bgolang\b|\bgo\s+language\b", "Go"),
    (r"\bphp\b", "PHP"),
    (r"\bsql\b|\bmysql\b|\bpostgresql\b", "SQL"),
    (r"\bmongodb\b", "MongoDB"),
    (r"\bhtml(?:\s*/\s*css|\s*5)?\b|\bcss(?:\s*3)?\b", "HTML/CSS"),
    (r"\bgit\b|\bgithub\b|\bgitlab\b", "Git"),
    (r"\bdocker\b|\bkubernetes\b", "Docker / Containers"),
    (r"\bcloud\b|\baws\b|\bgcp\b|\bazure\b", "Cloud Computing"),
    (r"\bmachine\s+learning\b|\bdeep\s+learning\b|\bartificial\s+intelligence\b|\bml\b|\bai\b", "Machine Learning / AI"),
    (r"\bdata\s+analysis\b|\bdata\s+analytics\b|\banalisis\s+data\b", "Data Analysis"),
    (r"\bdata\s+science\b|\bsains\s+data\b", "Data Science"),
    (r"\bui\s*/\s*ux\b|\bui/ux\b|\bfigma\b|\buser\s+experience\b", "UI/UX Design"),
    (r"\bcyber\s*security\b|\bkeamanan\s+siber\b", "Cybersecurity"),
    (r"\bmobile\s+dev(?:elopment)?\b|\bflutter\b|\breact\s+native\b|\bandroid\b|\bios\b", "Mobile Development"),
    
    # Soft skills & Languages
    (r"\benglish\b|\bbahasa\s+inggris\b", "English"),
    (r"\bleadership\b|\bkepemimpinan\b|\bjiwa\s+kepemimpinan\b", "Leadership"),
    (r"\bcommunication\b|\bkomunikasi\b|\bkemampuan\s+komunikasi\b", "Communication"),
    (r"\bpublic\s+speaking\b", "Public Speaking"),
    (r"\bteamwork\b|\bkerja\s*sama(?:\s+tim)?\b|\bkolaborasi\b|\bcollaboration\b", "Teamwork"),
    (r"\bproblem\s+solving\b|\bpemecahan\s+masalah\b", "Problem Solving"),
    (r"\bcritical\s+thinking\b|\bberpikir\s+kritis\b", "Critical Thinking"),
    (r"\bproject\s+management\b|\bmanajemen\s+proyek\b", "Project Management"),
    (r"\bresearch\b|\briset\b|\bpenelitian\b", "Research"),
    (r"\bwriting\b|\bpenulisan\b|\bcopywriting\b|\bcontent\s+writing\b", "Writing"),
    (r"\bgraphic\s+design\b|\bdesain\s+grafis\b", "Graphic Design"),
    (r"\bpresentation\b|\bpresentasi\b", "Presentation"),
]

# Required Documents Dictionary with regex patterns
DOCUMENT_PATTERNS = [
    (r"\bcv\b|\bcurriculum\s+vitae\b|\bresume\b", "Curriculum Vitae (CV) / Resume"),
    (r"\btranskrip(?:\s+nilai)?\b|\btranscript\b|\bacademic\s+transcript\b", "Academic Transcript"),
    (r"\bsurat\s+rekomendasi\b|\brecommendation\s+letter\b|\bletter\s+of\s+recommendation\b", "Recommendation Letter"),
    (r"\bmotivation\s+letter\b|\bsurat\s+motivasi\b|\bstatement\s+of\s+purpose\b|\bsop\b", "Motivation Letter / Statement of Purpose"),
    (r"\besai\b|\bessay\b", "Essay"),
    (r"\bportofolio\b|\bportfolio\b", "Portfolio"),
    (r"\bktm\b|\bkartu\s+tanda\s+mahasiswa\b|\bstudent\s+id\b", "Student ID (KTM)"),
    (r"\bktp\b|\bkartu\s+tanda\s+penduduk\b|\bid\s+card\b|\bidentitas\s+diri\b", "ID Card (KTP)"),
    (r"\btoefl\b|\bielts\b|\btoeic\b|\bduolingo\s+english\s+test\b|\bsertifikat\s+(?:kemampuan\s+)?bahasa(?:\s+inggris)?\b|\benglish\s+proficiency\s+certificate\b", "English Proficiency Certificate (TOEFL/IELTS)"),
    (r"\bsertifikat\s+prestasi\b|\bcertificate\s+of\s+achievement\b|\bsertifikat\s+penghargaan\b|\bsertifikat\b", "Certificates / Awards"),
    (r"\bsurat\s+keterangan\s+aktif\s+kuliah\b|\bcertificate\s+of\s+active\s+enrollment\b", "Certificate of Active Enrollment"),
    (r"\brancangan\s+studi\b|\bstudy\s+plan\b|\brencana\s+studi\b", "Study Plan / Proposal"),
    (r"\bsurat\s+keterangan\s+penghasilan\b|\bslip\s+gaji\b|\bfinancial\s+statement\b", "Financial Statement / Salary Slip"),
    (r"\bskck\b", "SKCK"),
    (r"\bpas\s*foto\b|\bphoto\b|\bfoto\s+(?:terbaru|3x4|4x6)\b", "Passport Photo"),
]

# Benefits Dictionary
BENEFIT_PATTERNS = [
    (r"\b(?:biaya\s+kuliah(?:\s+penuh)?|beasiswa\s+ukt|pembebasan\s+ukt|ukt|tuition\s+fee|full\s+tuition)\b", "Full / partial tuition fee (UKT)"),
    (r"\b(?:uang\s+saku(?:\s+bulanan)?|living\s+allowance|monthly\s+allowance|biaya\s+hidup|stipend|insentif(?:\s+bulanan)?)\b", "Monthly living allowance / Stipend"),
    (r"\b(?:tiket\s+pesawat|flight\s+tickets?|transportasi|transportation\s+allowance|biaya\s+transportasi)\b", "Transportation / Flight tickets"),
    (r"\b(?:akomodasi|tempat\s+tinggal|asrama|housing|accommodation)\b", "Accommodation / Housing"),
    (r"\b(?:asuransi\s+kesehatan|health\s+insurance|asuransi)\b", "Health insurance"),
    (r"\b(?:konversi\s+(?:ke\s+)?(?:hingga\s+)?(?:[0-9]+\s*)?sks|credit\s+conversion|20\s+sks)\b", "Academic credit conversion (SKS)"),
    (r"\b(?:mentoring|mentorship|bimbingan|pelatihan|training)\b", "Mentorship & Training"),
    (r"\b(?:networking|relasi|jaringan\s+profesional|professional\s+network)\b", "Networking opportunities"),
    (r"\b(?:hadiah\s*(?:uang|tunai|pembinaan)?|cash\s+prize|prize\s+pool|total\s+hadiah|dana\s+hibah|grant|funding)\b", "Cash prize / Funding grant"),
    (r"\b(?:sertifikat\s+resmi|sertifikat\s+penyelesaian|certificate\s+of\s+completion|official\s+certificate)\b", "Official Certificate of Completion"),
]


def extract_deadline(text: str) -> Optional[str]:
    """
    Extracts application/registration deadline from text.
    Handles Indonesian and English terms.
    """
    # 1. Broad Indonesian and English deadline prefixes
    deadline_prefix = (
        r"(?:"
        r"pendaftaran\s+(?:dibuka\s+)?sampai(?:\s+dengan)?"
        r"|pendaftaran\s+(?:terakhir|ditutup(?:\s+(?:pada|tanggal))?)"
        r"|batas\s+(?:akhir\s+)?pendaftaran"
        r"|batas\s+waktu(?:\s+pendaftaran)?"
        r"|tenggat\s+(?:waktu|pendaftaran)"
        r"|paling\s+lambat(?:\s+(?:tanggal|pada))?"
        r"|ditutup\s+(?:pada|tanggal)"
        r"|deadline\s+pendaftaran"
        r"|application\s+deadline"
        r"|registration\s+deadline"
        r"|submission\s+deadline"
        r"|due\s+date"
        r"|closing\s+date"
        r"|apply\s+before"
        r"|closes\s+on"
        r"|open\s+until"
        r"|deadline"
        r")"
    )

    # 2. Date patterns (Indonesian and English month names, or numeric dates)
    date_pattern = (
        r"(?:"
        r"[0-9]{1,2}\s+(?:Jan(?:uari)?|Feb(?:ruari)?|Mar(?:et)?|Apr(?:il)?|Mei|May|Jun(?:i)?|Jul(?:i)?|Agu(?:stus)?|Aug(?:ust)?|Sep(?:tember)?|Okt(?:ober)?|Oct(?:ober)?|Nov(?:ember)?|Des(?:ember)?|Dec(?:ember)?)(?:\s+[0-9]{4})?"
        r"|"
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+[0-9]{1,2}(?:st|nd|rd|th)?,?\s+[0-9]{4}"
        r"|"
        r"[0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4}"
        r"|"
        r"[0-9]{4}[-/][0-9]{1,2}[-/][0-9]{1,2}"
        r")"
    )

    # Priority 1: Prefix directly followed by a recognized date pattern
    match = re.search(
        rf"(?i){deadline_prefix}\s*[:\-–]?\s*(?:adalah\s*)?({date_pattern}(?:\s*\([^)]*\))?)",
        text,
    )
    if match:
        candidate = match.group(1).strip().lstrip(":-– ")
        if candidate and len(candidate) <= 60:
            return candidate

    # Priority 2: Prefix followed by general text up to punctuation / line break
    match_general = re.search(
        rf"(?i){deadline_prefix}\s*[:\-–]?\s*(?:adalah\s*)?([^\n\r,.;]{{3,50}})",
        text,
    )
    if match_general:
        candidate = match_general.group(1).strip().lstrip(":-– ")
        if candidate and len(candidate) <= 60:
            if candidate.lower().startswith("adalah"):
                candidate = candidate[6:].strip().lstrip(":-– ")
            if candidate and not re.match(r"(?i)^(adalah|yang|dan|atau|ini|tersebut)$", candidate):
                return candidate

    # Priority 3: Line-by-line fallback searching for deadline keywords and date on same line
    for line in text.splitlines():
        line_clean = line.strip()
        if re.search(
            r"(?i)\b(deadline|batas\s+(?:akhir\s+)?pendaftaran|tenggat|closing\s+date|due\s+date|paling\s+lambat|pendaftaran\s+(?:dibuka\s+)?sampai)\b",
            line_clean,
        ):
            date_match = re.search(date_pattern, line_clean, re.IGNORECASE)
            if date_match:
                return date_match.group(0).strip()
            parts = re.split(r"[:\-–]", line_clean, maxsplit=1)
            if len(parts) == 2 and 2 < len(parts[1].strip()) <= 50:
                candidate = parts[1].strip().rstrip(".,;")
                if candidate:
                    return candidate

    return None


def extract_minimum_gpa(text: str) -> Optional[str]:
    """
    Extracts minimum GPA or IPK requirement.
    Handles: "IPK minimal 3.25", "minimum GPA 3.50", "GPA >= 3.0", "IPK: 3.20".
    """
    patterns = [
        r"(?i)(?:minimal|minimum|min\.?)\s*(?:ipk|gpa)\s*(?:sebesar|adalah|of|:)?\s*([0-4][.,][0-9]{1,2})",
        r"(?i)(?:ipk|gpa)\s*(?:minimal|minimum|min\.?|>=|≥)?\s*(?:sebesar|adalah|of|:)?\s*([0-4][.,][0-9]{1,2})",
        r"(?i)\b(?:ipk|gpa)\b\s*[:\-–]?\s*([0-4][.,][0-9]{1,2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            raw_val = match.group(1).replace(",", ".").strip()
            try:
                f_val = float(raw_val)
                if 1.0 <= f_val <= 4.0:
                    # Format neatly with two decimals if needed
                    parts = raw_val.split(".")
                    if len(parts) == 2 and len(parts[1]) == 1:
                        return f"{f_val:.2f}"
                    return f"{f_val:.2f}" if "." in raw_val else str(int(f_val))
            except ValueError:
                pass
    return None


def extract_semester_requirement(text: str) -> Optional[str]:
    """
    Extracts semester requirement e.g. "Minimal Semester 5", "Semester 5 - 7", "Semester 3+".
    """
    # Range: e.g. "semester 5-7", "semester 4 sampai 6", "semester 3 to 5"
    range_match = re.search(
        r"(?i)\bsemester\s*([0-9]+\s*(?:-|–|sampai|to)\s*[0-9]+)\b",
        text
    )
    if range_match:
        raw_range = range_match.group(1).replace("–", "-")
        parts = re.split(r"-|sampai|to", raw_range, flags=re.IGNORECASE)
        if len(parts) == 2:
            return f"Semester {parts[0].strip()} - {parts[1].strip()}"
        return f"Semester {raw_range.strip()}"

    # Plus: e.g. "semester 3 ke atas", "semester 5+", "semester 4 dan keatas"
    plus_match = re.search(
        r"(?i)\bsemester\s*([0-9]+)\s*(?:ke\s*atas|\+|dan\s+keatas)\b",
        text
    )
    if plus_match:
        return f"Semester {plus_match.group(1).strip()}+"

    # Minimal: e.g. "minimal semester 5", "minimum semester 4"
    min_match = re.search(
        r"(?i)(?:minimal|minimum|min\.?)\s*semester\s*([0-9]+)\b",
        text
    )
    if min_match:
        return f"Minimal Semester {min_match.group(1).strip()}"

    # Student semester: e.g. "mahasiswa aktif semester 5", "student in semester 6"
    student_sem = re.search(
        r"(?i)(?:mahasiswa(?:\s+aktif)?|student)\s*semester\s*([0-9]+)\b",
        text
    )
    if student_sem:
        return f"Semester {student_sem.group(1).strip()}"

    # General semester: e.g. "Semester 5"
    general_sem = re.search(
        r"(?i)\bsemester\s*([0-9]+)\b",
        text
    )
    if general_sem:
        return f"Semester {general_sem.group(1).strip()}"

    return None


def extract_required_skills(text: str) -> List[str]:
    """
    Extracts recognized technical and soft skills present in the text.
    """
    found_skills: List[str] = []
    for pattern, canonical_name in SKILL_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if canonical_name not in found_skills:
                found_skills.append(canonical_name)
    return found_skills


def extract_required_documents(text: str) -> List[str]:
    """
    Extracts recognized required documents present in the text.
    """
    found_docs: List[str] = []
    has_language_cert = False

    for pattern, canonical_name in DOCUMENT_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if "TOEFL/IELTS" in canonical_name:
                has_language_cert = True
            # Avoid redundant generic "Certificates / Awards" if only language cert was found
            if canonical_name == "Certificates / Awards":
                # Check if it was explicitly mentioned as achievement/award cert or standalone cert
                if not re.search(r"(?i)\b(sertifikat\s+prestasi|sertifikat\s+penghargaan|certificate\s+of\s+achievement)\b", text):
                    # If only "sertifikat toefl" was in text, skip generic cert
                    if has_language_cert and not re.search(r"(?i)\b(sertifikat\s+(?:organisasi|seminar|pelatihan|keahlian))\b", text):
                        continue
            if canonical_name not in found_docs:
                found_docs.append(canonical_name)
    return found_docs


def extract_benefits(text: str) -> List[str]:
    """
    Extracts benefits and funding opportunities present in the text.
    """
    found_benefits: List[str] = []

    # 1. Match from canonical benefit patterns
    for pattern, canonical_name in BENEFIT_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if canonical_name not in found_benefits:
                found_benefits.append(canonical_name)

    # 2. Extract bullet items under a Benefit header if available
    lines = text.splitlines()
    in_benefit_section = False
    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        if re.match(r"(?i)^(?:benefits?|fasilitas|keuntungan|perks?|what\s+you(?:'ll|\s+will)\s+get)\s*[:\-–]?$", clean):
            in_benefit_section = True
            continue
        if in_benefit_section:
            # If hit another section header, stop
            if re.match(r"(?i)^[A-Za-z\s]+[:\-–]$", clean) and len(clean.split()) <= 4:
                in_benefit_section = False
                continue
            # Bullet point or dashed line
            bullet_match = re.match(r"^[-*•–+]\s*(.+)$", clean)
            if bullet_match:
                item = bullet_match.group(1).strip()
                if item and len(item) <= 90 and item not in found_benefits:
                    # Add custom bullet item if it provides valuable detail
                    found_benefits.append(item)

    # Deduplicate while preserving order
    unique_benefits: List[str] = []
    for b in found_benefits:
        if b not in unique_benefits:
            unique_benefits.append(b)

    return unique_benefits


def is_pure_gpa_requirement(text: str) -> bool:
    """
    Checks if a requirement line is solely an academic GPA requirement.
    These are already captured in the structured 'minimum_gpa' field.
    """
    clean = text.strip().lower()
    if re.search(r"\b(?:ipk|gpa)\b", clean):
        other_concepts = re.search(
            r"\b(?:mahasiswa\s+aktif|active\s+student|jurusan|prodi|major|wni|warga\s+negara|citizen|beasiswa\s+lain)\b",
            clean,
        )
        if not other_concepts:
            return True
    return False


def is_pure_semester_requirement(text: str) -> bool:
    """
    Checks if a requirement line is solely a semester requirement.
    These are already captured in the structured 'semester_requirement' field.
    """
    clean = text.strip().lower()
    if re.search(r"\bsemester\b", clean):
        other_concepts = re.search(
            r"\b(?:mahasiswa\s+aktif|active\s+(?:university\s+)?student|jurusan|prodi|major|wni|warga\s+negara|citizen|beasiswa|scholarship|ipk|gpa)\b",
            clean,
        )
        if not other_concepts:
            return True
    return False


def is_pure_skill_requirement(text: str) -> bool:
    """
    Checks if a requirement line is solely a skill proficiency statement.
    These are already captured in the structured 'required_skills' field.
    """
    clean = text.strip().lower()
    non_skill_keywords = re.search(
        r"\b(?:mahasiswa|student|wni|warga\s+negara|citizen|ipk|gpa|semester|jurusan|prodi|major|beasiswa\s+lain|sertifikat|dokumen|transkrip|surat)\b",
        clean,
    )
    if non_skill_keywords:
        return False

    skill_indicators = [
        r"\b(?:memiliki\s+)?kemampuan\b",
        r"\bmenguasai\b",
        r"\bkeahlian\b",
        r"\bproficient\s+in\b",
        r"\bfamiliar\s+with\b",
        r"\bstrong\s+knowledge\s+of\b",
        r"\bskills?\s+(?:in|of)\b",
        r"\bexperience\s+with\b",
        r"\bkompetensi\b",
    ]
    if any(re.search(pat, clean) for pat in skill_indicators):
        return True

    # Check if line consists solely of known skills
    clean_no_noise = re.sub(r"\b(?:dan|and|atau|or|serta|yang\s+baik)\b", "", clean)
    clean_tokens = [tok.strip() for tok in re.split(r"[,;/]", clean_no_noise) if tok.strip()]
    if clean_tokens:
        all_skills = True
        for tok in clean_tokens:
            if not any(re.search(pat, tok, re.IGNORECASE) for pat, _ in SKILL_PATTERNS):
                all_skills = False
                break
        if all_skills:
            return True

    return False


def is_pure_document_requirement(text: str) -> bool:
    """
    Checks if a requirement line is solely a document submission requirement.
    These are already captured in the structured 'required_documents' field.
    """
    clean = text.strip().lower()
    non_doc_keywords = re.search(
        r"\b(?:mahasiswa|student|wni|warga\s+negara|citizen|ipk|gpa|semester|jurusan|prodi|major|beasiswa\s+lain)\b",
        clean,
    )
    if non_doc_keywords:
        return False

    doc_indicators = [
        r"\b(?:melampirkan|mengunggah|unggah|kirimkan|submit|upload|attach)\b",
        r"\b(?:cv|curriculum\s+vitae|transkrip|transcript|surat\s+rekomendasi|recommendation\s+letter|portofolio|portfolio|esai|essay|motivational\s+letter|surat\s+motivasi|toefl|ielts)\b",
    ]
    if any(re.search(pat, clean) for pat in doc_indicators):
        if re.search(r"\b(?:cv|resume|transkrip|transcript|sertifikat|certificate|surat|letter|dokumen|document|berkas|file|esai|essay)\b", clean):
            return True
    return False


def normalize_eligibility_item(item: str) -> Optional[str]:
    """
    Normalizes a requirement string to a canonical eligibility criterion.
    Filters out pure GPA, pure semester, pure skills, and pure documents.
    Handles compound requirements (e.g., 'Mahasiswa aktif S1 minimal semester 5' -> 'Mahasiswa aktif S1').
    Returns canonical string or None if it should be excluded.
    """
    if not item:
        return None
    clean = item.strip()
    clean = re.sub(r"^[-*•–+\d\.)\s]+", "", clean).strip()
    if not clean:
        return None

    # Filter out pure structured criteria
    if is_pure_gpa_requirement(clean):
        return None
    if is_pure_semester_requirement(clean):
        return None
    if is_pure_skill_requirement(clean):
        return None
    if is_pure_document_requirement(clean):
        return None

    clean_lower = clean.lower()

    # 1. Citizenship / Nationality
    if re.search(r"\b(?:wni|warga\s+negara\s+indonesia|indonesian\s+citizen)\b", clean_lower):
        return "Indonesian Citizen (WNI)"

    # 2. Scholarship restriction
    if re.search(r"\b(?:tidak\s+sedang\s+menerima\s+beasiswa|not\s+(?:currently\s+)?receiving\s+other\s+scholarships?)\b", clean_lower):
        return "Not currently receiving other scholarships"

    # 3. Open to all majors
    if re.search(r"\b(?:terbuka\s+untuk\s+semua\s+(?:jurusan|program\s+studi)|semua\s+jurusan|open\s+to\s+all\s+majors)\b", clean_lower):
        return "Open to all study programs / majors"

    # 4. Active student status (strips embedded semester constraints to avoid duplication)
    if re.search(r"\b(?:mahasiswa\s+aktif|active\s+(?:university\s+)?student)\b", clean_lower):
        degree_match = re.search(r"\b(s1|d4|d3|s2)\b", clean_lower)
        if degree_match:
            degree = degree_match.group(1).upper()
            major_match = re.search(r"(?i)\b(?:jurusan|program\s+studi|prodi|major)\s+([A-Za-z\s]+)", clean)
            if major_match:
                return f"Mahasiswa aktif {degree} ({major_match.group(0).strip()})"
            return f"Mahasiswa aktif {degree}"
        else:
            return "Active university student"

    # 5. Length check for custom requirements
    if len(clean) > 100:
        return None

    return clean


def deduplicate_eligibility_list(items: List[str]) -> List[str]:
    """
    Deduplicates normalized eligibility items using semantic keys.
    If a specific active student degree (e.g., 'Mahasiswa aktif S1') is present,
    it supersedes the generic 'Active university student'.
    Preserves insertion order.
    """
    has_specific_student = any(
        re.search(r"\bmahasiswa\s+aktif\s+(?:s1|d4|d3|s2)\b", it, re.IGNORECASE)
        for it in items
    )

    seen_keys = set()
    deduped: List[str] = []

    for item in items:
        if not item:
            continue
        clean = item.strip()
        clean_lower = clean.lower()

        # If specific degree exists, skip generic active student
        if has_specific_student and clean_lower in ["active university student", "mahasiswa aktif perguruan tinggi"]:
            continue

        # Semantic key mapping
        if re.search(r"\b(?:wni|warga\s+negara\s+indonesia|indonesian\s+citizen)\b", clean_lower):
            key = "eligibility:citizenship:wni"
        elif re.search(r"\bmahasiswa\s+aktif\s+(s1|d4|d3|s2)\b", clean_lower):
            deg = re.search(r"\bmahasiswa\s+aktif\s+(s1|d4|d3|s2)\b", clean_lower).group(1).lower()
            key = f"eligibility:active_student:{deg}"
        elif re.search(r"\b(?:mahasiswa\s+aktif|active\s+(?:university\s+)?student)\b", clean_lower):
            key = "eligibility:active_student:general"
        elif re.search(r"\b(?:tidak\s+sedang\s+menerima\s+beasiswa|not\s+(?:currently\s+)?receiving\s+other\s+scholarships?)\b", clean_lower):
            key = "eligibility:other_scholarships"
        elif re.search(r"\b(?:terbuka\s+untuk\s+semua\s+(?:jurusan|program\s+studi)|semua\s+jurusan|open\s+to\s+all\s+majors)\b", clean_lower):
            key = "eligibility:open_all_majors"
        else:
            key = re.sub(r"[^a-z0-9]", "", clean_lower)

        if key not in seen_keys:
            seen_keys.add(key)
            deduped.append(clean)

    return deduped


def extract_eligibility(
    text: str,
    minimum_gpa: Optional[str] = None,
    semester_req: Optional[str] = None
) -> List[str]:
    """
    Extracts canonical eligibility requirements present in the text.
    Avoids duplicating structured fields (minimum_gpa, semester_requirement,
    required_skills, required_documents) as generic eligibility entries.
    """
    raw_items: List[str] = []

    # 1. Active student status from overview text
    if re.search(r"(?i)\b(?:mahasiswa\s+aktif(?:\s+(?:s1|d4|d3|s2))?|active\s+(?:university\s+)?student)\b", text):
        match = re.search(r"(?i)\bmahasiswa\s+aktif\s+(s1|d4|d3|s2)\b", text)
        if match:
            raw_items.append(f"Mahasiswa aktif {match.group(1).upper()}")
        else:
            raw_items.append("Active university student")

    # 2. Nationality / Citizenship
    if re.search(r"(?i)\b(?:wni|warga\s+negara\s+indonesia|indonesian\s+citizen)\b", text):
        raw_items.append("Indonesian Citizen (WNI)")

    # 3. Not receiving other scholarships
    if re.search(r"(?i)\b(?:tidak\s+sedang\s+menerima\s+beasiswa|not\s+(?:currently\s+)?receiving\s+other\s+scholarships?)\b", text):
        raw_items.append("Not currently receiving other scholarships")

    # 4. Major / Study program
    if re.search(r"(?i)\b(?:terbuka\s+untuk\s+semua\s+(?:jurusan|program\s+studi)|semua\s+jurusan|open\s+to\s+all\s+majors)\b", text):
        raw_items.append("Open to all study programs / majors")

    # Note: minimum_gpa and semester_req are intentionally NOT appended here
    # because they have dedicated structured fields and scoring categories.

    # 5. Extract bullet points under an Eligibility / Requirements header
    lines = text.splitlines()
    in_req_section = False
    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        if re.match(r"(?i)^(?:eligibility|requirements?|persyaratan|kriteria|syarat(?:\s+pendaftaran)?)\s*[:\-–]?$", clean):
            in_req_section = True
            continue
        if in_req_section:
            if re.match(r"(?i)^[A-Za-z\s]+[:\-–]$", clean) and len(clean.split()) <= 4:
                in_req_section = False
                continue
            bullet_match = re.match(r"^[-*•–+]\s*(.+)$", clean)
            if bullet_match:
                item = bullet_match.group(1).strip()
                normalized = normalize_eligibility_item(item)
                if normalized:
                    raw_items.append(normalized)

    # 6. Apply semantic deduplication
    return deduplicate_eligibility_list(raw_items)


def analyze_opportunity(opportunity_type: str, description: str) -> Dict[str, Any]:
    """
    Main lightweight deterministic analyzer for extracting structured information
    from an opportunity description without external AI APIs.
    """
    clean_desc = description.strip()

    deadline = extract_deadline(clean_desc)
    minimum_gpa = extract_minimum_gpa(clean_desc)
    semester_req = extract_semester_requirement(clean_desc)
    required_skills = extract_required_skills(clean_desc)
    required_documents = extract_required_documents(clean_desc)
    benefits = extract_benefits(clean_desc)
    eligibility = extract_eligibility(clean_desc, minimum_gpa=minimum_gpa, semester_req=semester_req)

    return {
        "opportunity_type": opportunity_type,
        "analysis": {
            "deadline": deadline,
            "minimum_gpa": minimum_gpa,
            "semester_requirement": semester_req,
            "required_skills": required_skills,
            "required_documents": required_documents,
            "benefits": benefits,
            "eligibility": eligibility,
        },
    }
