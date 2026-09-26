import { useState } from "react";

function ProfileForm() {
  const [profile, setProfile] = useState({
    studyProgram: "",
    semester: "",
    gpa: "",
    skills: "",
    experience: "",
  });

  function handleChange(event) {
    const { name, value } = event.target;
    setProfile((current) => ({ ...current, [name]: value }));
  }

  return (
    <form className="form" onSubmit={(event) => event.preventDefault()}>
      <div className="field">
        <label htmlFor="studyProgram">Study Program</label>
        <input
          id="studyProgram"
          name="studyProgram"
          type="text"
          autoComplete="off"
          placeholder="Informatics Engineering"
          value={profile.studyProgram}
          onChange={handleChange}
        />
      </div>

      <div className="field-row">
        <div className="field">
          <label htmlFor="semester">Semester</label>
          <input
            id="semester"
            name="semester"
            type="text"
            inputMode="numeric"
            placeholder="5"
            value={profile.semester}
            onChange={handleChange}
          />
        </div>
        <div className="field">
          <label htmlFor="gpa">GPA</label>
          <input
            id="gpa"
            name="gpa"
            type="text"
            inputMode="decimal"
            placeholder="3.52"
            value={profile.gpa}
            onChange={handleChange}
          />
        </div>
      </div>

      <div className="field">
        <label htmlFor="skills">Skills</label>
        <input
          id="skills"
          name="skills"
          type="text"
          placeholder="Python, React, Cloud, Cybersecurity..."
          value={profile.skills}
          onChange={handleChange}
        />
      </div>

      <div className="field">
        <label htmlFor="experience">Experience &amp; Achievements</label>
        <textarea
          id="experience"
          name="experience"
          rows="5"
          placeholder="Organizations, projects, internships, certifications, competitions..."
          value={profile.experience}
          onChange={handleChange}
        />
      </div>
    </form>
  );
}

export default ProfileForm;
