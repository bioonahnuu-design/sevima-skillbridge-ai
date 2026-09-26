function OpportunityAnalysis({ data }) {
  if (!data) return null;

  const { opportunity_type, analysis } = data;
  const {
    deadline,
    minimum_gpa,
    semester_requirement,
    required_skills = [],
    required_documents = [],
    benefits = [],
    eligibility = [],
  } = analysis || {};

  return (
    <section className="snapshot-container" aria-labelledby="snapshot-heading">
      <div className="snapshot-header-row">
        <span className="snapshot-eyebrow">OPPORTUNITY SNAPSHOT</span>
        {opportunity_type && (
          <span className="snapshot-type-pill">{opportunity_type}</span>
        )}
      </div>

      {/* Primary 4-Cell Criteria Grid with Subtle Dividers */}
      <div className="snapshot-metrics-grid">
        <div className="snapshot-metric-item">
          <span className="snapshot-metric-label">OPPORTUNITY TYPE</span>
          <span className="snapshot-metric-value snapshot-metric-title">
            {opportunity_type || "General Opportunity"}
          </span>
        </div>

        <div className="snapshot-metric-item">
          <span className="snapshot-metric-label">APPLICATION DEADLINE</span>
          <span className={`snapshot-metric-value ${deadline ? "val-highlight" : "val-muted"}`}>
            {deadline || "Not specified"}
          </span>
        </div>

        <div className="snapshot-metric-item">
          <span className="snapshot-metric-label">MINIMUM GPA</span>
          <span className={`snapshot-metric-value ${minimum_gpa ? "val-highlight" : "val-muted"}`}>
            {minimum_gpa ? `≥ ${minimum_gpa}` : "None specified"}
          </span>
        </div>

        <div className="snapshot-metric-item">
          <span className="snapshot-metric-label">SEMESTER</span>
          <span className={`snapshot-metric-value ${semester_requirement ? "val-highlight" : "val-muted"}`}>
            {semester_requirement || "Open to all semesters"}
          </span>
        </div>
      </div>

      {/* Editorial Requirement Rows with Subtle Dividers */}
      <div className="snapshot-details-list">
        {/* Required Skills */}
        <div className="snapshot-detail-row">
          <div className="snapshot-detail-label">REQUIRED SKILLS</div>
          <div className="snapshot-detail-content">
            {required_skills.length > 0 ? (
              <span className="snapshot-inline-items">
                {required_skills.join(" · ")}
              </span>
            ) : (
              <span className="snapshot-empty-note">
                No specific technical or soft skills stated.
              </span>
            )}
          </div>
        </div>

        {/* Required Documents */}
        <div className="snapshot-detail-row">
          <div className="snapshot-detail-label">REQUIRED DOCUMENTS</div>
          <div className="snapshot-detail-content">
            {required_documents.length > 0 ? (
              <span className="snapshot-inline-items">
                {required_documents.join(" · ")}
              </span>
            ) : (
              <span className="snapshot-empty-note">
                No mandatory document submission listed.
              </span>
            )}
          </div>
        </div>

        {/* Eligibility */}
        <div className="snapshot-detail-row">
          <div className="snapshot-detail-label">ELIGIBILITY</div>
          <div className="snapshot-detail-content">
            {eligibility.length > 0 ? (
              <span className="snapshot-inline-items">
                {eligibility.join(" · ")}
              </span>
            ) : (
              <span className="snapshot-empty-note">
                General eligibility criteria apply.
              </span>
            )}
          </div>
        </div>

        {/* Benefits & Funding */}
        <div className="snapshot-detail-row">
          <div className="snapshot-detail-label">BENEFITS &amp; FUNDING</div>
          <div className="snapshot-detail-content">
            {benefits.length > 0 ? (
              <span className="snapshot-inline-items">
                {benefits.join(" · ")}
              </span>
            ) : (
              <span className="snapshot-empty-note">
                Funding details not explicitly stated.
              </span>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

export default OpportunityAnalysis;
