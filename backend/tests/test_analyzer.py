from app.services.analyzer import (
    analyze_opportunity,
    extract_deadline,
    extract_minimum_gpa,
    extract_semester_requirement,
    extract_required_skills,
    extract_required_documents,
    extract_benefits,
    extract_eligibility,
)


def test_extract_deadline():
    text_id = "Pendaftaran dibuka sampai 15 Oktober 2025. Harap kirimkan berkas."
    assert extract_deadline(text_id) is not None

    text_en = "Application Deadline: December 1, 2025."
    assert "December 1, 2025" in extract_deadline(text_en)

    text_none = "Tidak ada tanggal di sini."
    assert extract_deadline(text_none) is None


def test_extract_minimum_gpa():
    text_id = "Syarat pendaftaran memiliki IPK minimal 3.25 skala 4.00"
    assert extract_minimum_gpa(text_id) == "3.25"

    text_en = "Minimum GPA of 3.5 is required."
    assert extract_minimum_gpa(text_en) == "3.50"

    text_comma = "IPK minimal 3,00"
    assert extract_minimum_gpa(text_comma) == "3.00"

    text_none = "Terbuka untuk semua mahasiswa berprestasi."
    assert extract_minimum_gpa(text_none) is None


def test_extract_semester_requirement():
    text_range = "Terbuka bagi mahasiswa semester 5 - 7 yang berminat."
    assert extract_semester_requirement(text_range) == "Semester 5 - 7"

    text_min = "Minimal semester 4 saat mendaftar program ini."
    assert extract_semester_requirement(text_min) == "Minimal Semester 4"

    text_plus = "Mahasiswa semester 3 ke atas dapat mendaftar."
    assert extract_semester_requirement(text_plus) == "Semester 3+"

    text_none = "Terbuka untuk umum."
    assert extract_semester_requirement(text_none) is None


def test_extract_skills():
    text = "Kandidat diharapkan menguasai Python, React, dan memiliki kemampuan communication serta teamwork yang baik."
    skills = extract_required_skills(text)
    assert "Python" in skills
    assert "React" in skills
    assert "Communication" in skills
    assert "Teamwork" in skills
    assert "Java" not in skills


def test_extract_documents():
    text = "Kirimkan CV terbaru, transkrip nilai, sertifikat TOEFL, dan surat rekomendasi dosen."
    docs = extract_required_documents(text)
    assert "Curriculum Vitae (CV) / Resume" in docs
    assert "Academic Transcript" in docs
    assert "English Proficiency Certificate (TOEFL/IELTS)" in docs
    assert "Recommendation Letter" in docs


def test_extract_benefits():
    text = "Fasilitas: Beasiswa UKT penuh, uang saku bulanan, konversi 20 SKS, dan bimbingan mentor."
    benefits = extract_benefits(text)
    assert any("tuition" in b.lower() or "ukt" in b.lower() for b in benefits)
    assert any("allowance" in b.lower() or "stipend" in b.lower() for b in benefits)
    assert any("sks" in b.lower() for b in benefits)
    assert any("mentorship" in b.lower() for b in benefits)


def test_analyze_opportunity_realistic():
    desc = """
    Beasiswa Prestasi Cendekia 2025
    Batas pendaftaran: 25 November 2025
    Syarat:
    - Mahasiswa aktif S1 minimal semester 5
    - IPK minimal 3.30
    - WNI
    - Memiliki kemampuan bahasa Inggris dan leadership
    - Menguasai Python atau Data Analysis
    Dokumen:
    - CV, transkrip nilai, sertifikat prestasi, dan esai
    Benefit:
    - Pembebasan UKT
    - Uang saku bulanan
    - Mentoring profesional
    """
    res = analyze_opportunity("Scholarship", desc)
    assert res["opportunity_type"] == "Scholarship"
    analysis = res["analysis"]
    assert analysis["minimum_gpa"] == "3.30"
    assert "Minimal Semester 5" in analysis["semester_requirement"]
    assert "Python" in analysis["required_skills"]
    assert "English" in analysis["required_skills"]
    assert "Curriculum Vitae (CV) / Resume" in analysis["required_documents"]
    assert "Essay" in analysis["required_documents"]
    assert any("ukt" in b.lower() or "tuition" in b.lower() for b in analysis["benefits"])
    assert any("allowance" in b.lower() or "stipend" in b.lower() for b in analysis["benefits"])


def test_wni_variants_no_duplicate_eligibility():
    desc = """
    Beasiswa Indonesia Maju
    Syarat:
    - Warga Negara Indonesia (WNI)
    - Indonesian Citizen (WNI)
    """
    res = analyze_opportunity("Scholarship", desc)
    eligibility = res["analysis"]["eligibility"]
    wni_items = [e for e in eligibility if "wni" in e.lower() or "indonesian citizen" in e.lower()]
    assert len(wni_items) == 1
    assert wni_items[0] == "Indonesian Citizen (WNI)"


def test_gpa_not_duplicated_in_eligibility():
    desc = """
    Program Pertukaran Mahasiswa
    Syarat:
    - IPK minimal 3.25 skala 4.00
    - Mahasiswa aktif S1
    """
    res = analyze_opportunity("Exchange", desc)
    assert res["analysis"]["minimum_gpa"] == "3.25"
    eligibility = res["analysis"]["eligibility"]
    assert not any("ipk" in e.lower() or "gpa" in e.lower() for e in eligibility)
    assert "Mahasiswa aktif S1" in eligibility


def test_semester_not_duplicated_in_eligibility():
    desc = """
    Magang Riset Nasional
    Syarat:
    - Minimal semester 5
    - Mahasiswa aktif S1
    """
    res = analyze_opportunity("Internship", desc)
    assert "Semester 5" in res["analysis"]["semester_requirement"]
    eligibility = res["analysis"]["eligibility"]
    assert not any("semester" in e.lower() for e in eligibility)
    assert "Mahasiswa aktif S1" in eligibility


def test_skill_only_not_duplicated_in_eligibility():
    desc = """
    Lomba UI/UX Design
    Syarat:
    - Memiliki kemampuan Python dan Leadership
    - Menguasai React
    - Mahasiswa aktif S1
    """
    res = analyze_opportunity("Competition", desc)
    skills = res["analysis"]["required_skills"]
    assert "Python" in skills
    assert "Leadership" in skills
    assert "React" in skills
    eligibility = res["analysis"]["eligibility"]
    assert not any("kemampuan" in e.lower() or "menguasai" in e.lower() for e in eligibility)
    assert not any("python" in e.lower() or "leadership" in e.lower() or "react" in e.lower() for e in eligibility)
    assert "Mahasiswa aktif S1" in eligibility


def test_mahasiswa_aktif_minimal_semester_preserves_active_student():
    desc = """
    Program Beasiswa Unggulan
    Syarat:
    - Mahasiswa aktif S1 minimal semester 5
    """
    res = analyze_opportunity("Scholarship", desc)
    assert "Semester 5" in res["analysis"]["semester_requirement"]
    eligibility = res["analysis"]["eligibility"]
    assert len(eligibility) == 1
    assert eligibility[0] == "Mahasiswa aktif S1"

