function ProfileForm({ profile, onChange }) {
  const currentProfile = profile || {
    studyProgram: "",
    semester: "",
    gpa: "",
    skills: "",
    experience: "",
  };

  function handleChange(event) {
    const { name, value } = event.target;
    if (onChange) {
      onChange(name, value);
    }
  }

  return (
    <form className="workspace-form form" onSubmit={(event) => event.preventDefault()}>
      <div className="form-group field">
        <label htmlFor="studyProgram" className="form-label">
          <span>Study Program / Major</span>
          <span className="form-hint">Program Studi</span>
        </label>
        <input
          id="studyProgram"
          name="studyProgram"
          type="text"
          className="form-input"
          autoComplete="off"
          placeholder="e.g. Informatics Engineering, Akuntansi, Manajemen"
          value={currentProfile.studyProgram}
          onChange={handleChange}
        />
      </div>

      <div className="form-row field-row">
        <div className="form-group form-col field">
          <label htmlFor="semester" className="form-label">
            <span>Current Semester</span>
            <span className="form-hint">Semester Aktif</span>
          </label>
          <input
            id="semester"
            name="semester"
            type="text"
            inputMode="numeric"
            className="form-input"
            placeholder="e.g. 5"
            value={currentProfile.semester}
            onChange={handleChange}
          />
        </div>
        <div className="form-group form-col field">
          <label htmlFor="gpa" className="form-label">
            <span>Current GPA</span>
            <span className="form-hint">IPK Kumulatif (0 - 4.00)</span>
          </label>
          <input
            id="gpa"
            name="gpa"
            type="text"
            inputMode="decimal"
            className="form-input"
            placeholder="e.g. 3.52"
            value={currentProfile.gpa}
            onChange={handleChange}
          />
        </div>
      </div>

      <div className="form-group field">
        <label htmlFor="skills" className="form-label">
          <span>Skills &amp; Competencies</span>
          <span className="form-hint">Keahlian (pisahkan koma)</span>
        </label>
        <input
          id="skills"
          name="skills"
          type="text"
          className="form-input"
          placeholder="e.g. Python, React, Cloud, Data Analysis, Leadership..."
          value={currentProfile.skills}
          onChange={handleChange}
        />
      </div>

      <div className="form-group field">
        <label htmlFor="experience" className="form-label">
          <span>Experience &amp; Achievements</span>
          <span className="form-hint">Pengalaman &amp; Prestasi</span>
        </label>
        <textarea
          id="experience"
          name="experience"
          className="form-textarea"
          rows="5"
          placeholder="Organizations, projects, internships, certifications, competitions, leadership roles..."
          value={currentProfile.experience}
          onChange={handleChange}
        />
      </div>
    </form>
  );
}

export default ProfileForm;
