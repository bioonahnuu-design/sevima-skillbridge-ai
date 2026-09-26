function formatStatusBadge(status) {
  switch (status) {
    case "matched":
      return { label: "Matched", className: "status-pill status-matched" };
    case "partial":
      return { label: "Partial Fit", className: "status-pill status-partial" };
    case "missing":
      return { label: "Missing", className: "status-pill status-missing" };
    case "needs_verification":
      return {
        label: "Needs Verification",
        className: "status-pill status-verify",
      };
    case "upcoming":
      return { label: "Upcoming", className: "status-pill status-upcoming" };
    case "today":
      return { label: "Today", className: "status-pill status-today" };
    case "passed":
      return { label: "Passed", className: "status-pill status-passed" };
    case "not_specified":
    default:
      return {
        label: "Not Specified",
        className: "status-pill status-unspecified",
      };
  }
}

function ProfileMatch({ data }) {
  if (!data) return null;

  const {
    match_score = 0,
    summary = "",
    breakdown = {},
    matched = [],
    gaps = [],
    needs_verification = [],
  } = data;

  const categories = [
    { key: "eligibility", title: "Eligibility", weight: 40, icon: "🎯" },
    { key: "academic", title: "Academic Fit", weight: 20, icon: "🎓" },
    { key: "skills", title: "Skills Fit", weight: 15, icon: "⚡" },
    { key: "documents", title: "Document Readiness", weight: 15, icon: "📄" },
    { key: "deadline", title: "Deadline Readiness", weight: 10, icon: "⏱" },
  ];

  return (
    <section className="match-section" aria-labelledby="match-score-heading">
      <article className="card match-card">
        {/* Header & Match Score Hero */}
        <div className="match-hero">
          <div className="score-badge-container">
            <div className="score-large">{match_score}%</div>
            <div className="score-tag">Profile Match</div>
          </div>

          <div className="match-hero-info">
            <div className="match-pill-row">
              <span className="step-label">CORE FEATURE 02</span>
              <span className="copilot-pill">Evaluation Complete</span>
            </div>
            <h2 id="match-score-heading" className="match-title">
              Profile Match Score
            </h2>
            <p className="match-disclaimer">
              This score reflects how closely your current profile matches the
              requirements we could evaluate.
            </p>
            {summary && <p className="match-summary-callout">{summary}</p>}
          </div>
        </div>

        {/* Category Breakdown Grid */}
        <div className="breakdown-wrapper">
          <h3 className="section-subheading">Match Breakdown</h3>
          <div className="breakdown-grid">
            {categories.map((cat) => {
              const catData = breakdown[cat.key] || {
                weight: cat.weight,
                status: "not_specified",
                score: null,
                detail: "",
              };
              const badge = formatStatusBadge(catData.status);

              return (
                <div key={cat.key} className="breakdown-card">
                  <div className="breakdown-card-top">
                    <span className="cat-icon" aria-hidden="true">
                      {cat.icon}
                    </span>
                    <span className={badge.className}>{badge.label}</span>
                  </div>

                  <h4 className="breakdown-card-title">{cat.title}</h4>
                  <div className="breakdown-weight-row">
                    <span className="weight-label">Weight: {cat.weight}%</span>
                    <span className="score-earned">
                      {catData.score !== null
                        ? `${catData.score} pts`
                        : "Unscored"}
                    </span>
                  </div>

                  {catData.detail && (
                    <p className="breakdown-detail">{catData.detail}</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Gap Analysis Section */}
        <div className="gaps-wrapper">
          <div className="gaps-header-row">
            <h3 className="section-subheading">Gap Analysis</h3>
            <span className="gaps-count-pill">
              {gaps.length} Gap{gaps.length === 1 ? "" : "s"} Identified
            </span>
          </div>

          <div className="gap-columns">
            {/* Gaps / Missing Items */}
            <div className="gap-column">
              <h4 className="column-title column-title-gaps">
                <span className="col-bullet col-bullet-gap" aria-hidden="true">
                  !
                </span>
                Identified Gaps ({gaps.length})
              </h4>
              {gaps.length > 0 ? (
                <ul className="gap-item-list">
                  {gaps.map((item, idx) => (
                    <li key={idx} className="gap-entry gap-entry-missing">
                      <div className="gap-entry-header">
                        <span className="gap-category-tag">
                          {item.category}
                        </span>
                        <span className="gap-status-pill status-missing">
                          Missing
                        </span>
                      </div>
                      <p className="gap-entry-message">{item.message}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="empty-subtext">
                  No missing criteria found in evaluated categories!
                </p>
              )}
            </div>

            {/* Matched Criteria */}
            <div className="gap-column">
              <h4 className="column-title column-title-matched">
                <span
                  className="col-bullet col-bullet-matched"
                  aria-hidden="true"
                >
                  ✓
                </span>
                Matched Criteria ({matched.length})
              </h4>
              {matched.length > 0 ? (
                <ul className="gap-item-list">
                  {matched.map((item, idx) => (
                    <li key={idx} className="gap-entry gap-entry-satisfied">
                      <div className="gap-entry-header">
                        <span className="gap-category-tag">
                          {item.category}
                        </span>
                        <span className="gap-status-pill status-matched">
                          Satisfied
                        </span>
                      </div>
                      <p className="gap-entry-message">{item.message}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="empty-subtext">
                  No criteria evaluated as matched yet.
                </p>
              )}
            </div>

            {/* Needs Verification */}
            <div className="gap-column">
              <h4 className="column-title column-title-verify">
                <span
                  className="col-bullet col-bullet-verify"
                  aria-hidden="true"
                >
                  ?
                </span>
                Needs Verification ({needs_verification.length})
              </h4>
              {needs_verification.length > 0 ? (
                <ul className="gap-item-list">
                  {needs_verification.map((item, idx) => (
                    <li key={idx} className="gap-entry gap-entry-verify">
                      <div className="gap-entry-header">
                        <span className="gap-category-tag">
                          {item.category}
                        </span>
                        <span className="gap-status-pill status-verify">
                          To Verify
                        </span>
                      </div>
                      <p className="gap-entry-message">{item.message}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="empty-subtext">
                  All requirements could be directly evaluated.
                </p>
              )}
            </div>
          </div>
        </div>
      </article>
    </section>
  );
}

export default ProfileMatch;
