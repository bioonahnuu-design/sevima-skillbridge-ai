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
    <section className="analysis-section" aria-labelledby="analysis-heading">
      <article className="card analysis-card">
        <header className="card-header analysis-card-header">
          <div className="card-icon card-icon-spark" aria-hidden="true">
            <span className="spark">✦</span>
          </div>
          <div className="analysis-header-text">
            <div className="analysis-badge-row">
              <p className="step-label">CORE FEATURE 01</p>
              {opportunity_type && (
                <span className="type-badge">{opportunity_type}</span>
              )}
            </div>
            <h2 id="analysis-heading">Opportunity Analysis</h2>
            <p className="card-subtitle">
              Structured breakdown of requirements, eligibility, deadlines, and
              benefits extracted from the opportunity description.
            </p>
          </div>
        </header>

        {/* Quick parameters overview grid */}
        <div className="analysis-overview-grid">
          <div className="overview-item">
            <span className="overview-label">Opportunity Type</span>
            <span className="overview-value">
              {opportunity_type || "Not specified"}
            </span>
          </div>

          <div className="overview-item">
            <span className="overview-label">Application Deadline</span>
            <span
              className={
                deadline ? "overview-value" : "overview-value overview-empty"
              }
            >
              {deadline || "Not specified"}
            </span>
          </div>

          <div className="overview-item">
            <span className="overview-label">Minimum GPA</span>
            <span
              className={
                minimum_gpa ? "overview-value" : "overview-value overview-empty"
              }
            >
              {minimum_gpa ? `≥ ${minimum_gpa}` : "Not specified"}
            </span>
          </div>

          <div className="overview-item">
            <span className="overview-label">Semester Requirement</span>
            <span
              className={
                semester_requirement
                  ? "overview-value"
                  : "overview-value overview-empty"
              }
            >
              {semester_requirement || "Not specified"}
            </span>
          </div>
        </div>

        {/* Detailed breakdown 2-column grid */}
        <div className="analysis-details-grid">
          {/* Required Skills */}
          <div className="detail-panel">
            <h3 className="detail-panel-title">
              <span className="panel-icon" aria-hidden="true">
                ⚡
              </span>
              Required Skills
            </h3>
            {required_skills.length > 0 ? (
              <div className="tags-container">
                {required_skills.map((skill, index) => (
                  <span key={index} className="skill-chip">
                    {skill}
                  </span>
                ))}
              </div>
            ) : (
              <p className="not-specified">Not specified</p>
            )}
          </div>

          {/* Required Documents */}
          <div className="detail-panel">
            <h3 className="detail-panel-title">
              <span className="panel-icon" aria-hidden="true">
                📄
              </span>
              Required Documents
            </h3>
            {required_documents.length > 0 ? (
              <ul className="doc-list">
                {required_documents.map((doc, index) => (
                  <li key={index} className="doc-item">
                    <span className="item-bullet" aria-hidden="true">
                      ✓
                    </span>
                    <span>{doc}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="not-specified">Not specified</p>
            )}
          </div>

          {/* Eligibility Requirements */}
          <div className="detail-panel">
            <h3 className="detail-panel-title">
              <span className="panel-icon" aria-hidden="true">
                🎯
              </span>
              Eligibility Requirements
            </h3>
            {eligibility.length > 0 ? (
              <ul className="doc-list">
                {eligibility.map((item, index) => (
                  <li key={index} className="doc-item">
                    <span className="item-bullet" aria-hidden="true">
                      ✓
                    </span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="not-specified">Not specified</p>
            )}
          </div>

          {/* Benefits / Funding */}
          <div className="detail-panel">
            <h3 className="detail-panel-title">
              <span className="panel-icon" aria-hidden="true">
                🎁
              </span>
              Benefits &amp; Funding
            </h3>
            {benefits.length > 0 ? (
              <ul className="doc-list">
                {benefits.map((benefit, index) => (
                  <li key={index} className="doc-item">
                    <span className="item-bullet" aria-hidden="true">
                      ✓
                    </span>
                    <span>{benefit}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="not-specified">Not specified</p>
            )}
          </div>
        </div>
      </article>
    </section>
  );
}

export default OpportunityAnalysis;
