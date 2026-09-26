function GapAnalysis({ data }) {
  if (!data) return null;

  const {
    gaps = [],
    matched = [],
    needs_verification = [],
  } = data;

  return (
    <section className="gap-report-container" aria-labelledby="gap-analysis-title">
      {/* Header */}
      <div className="gap-report-header">
        <span className="gap-eyebrow">DIAGNOSTIC GAP ANALYSIS</span>
        <h2 id="gap-analysis-title" className="gap-title">
          What's holding you back?
        </h2>
        <p className="gap-subtitle">
          Direct comparison between the opportunity's strict requirements and your student profile.
        </p>
      </div>

      {/* Dominant NEEDS ATTENTION Block */}
      <div className="needs-attention-block">
        <div className="attention-header-bar">
          <div className="attention-tag-group">
            <span className="attention-bullet" aria-hidden="true">!</span>
            <span className="attention-label">CRITICAL ATTENTION REQUIRED</span>
          </div>
          <span className="attention-count-tag">
            {gaps.length} {gaps.length === 1 ? "Gap Identified" : "Gaps Identified"}
          </span>
        </div>

        {gaps.length === 0 ? (
          <div className="attention-empty-state">
            <span className="empty-check-icon" aria-hidden="true">✓</span>
            <div>
              <div className="empty-strong">No critical gaps detected!</div>
              <div className="empty-sub">
                Your profile satisfies all core explicit criteria for this opportunity.
              </div>
            </div>
          </div>
        ) : (
          <div className="attention-items-stack">
            {gaps.map((item, idx) => {
              const reqText = item.requirement || item.item || item.label || "Requirement";
              const reasonText = item.message || item.reason || "";
              const categoryText = item.category || "";

              return (
                <div key={idx} className="attention-row">
                  <span className="attention-num">
                    #{String(idx + 1).padStart(2, "0")}
                  </span>
                  <div className="attention-body-col">
                    <div className="attention-req-row">
                      <span className="attention-req-name">{reqText}</span>
                      {categoryText && (
                        <span className="attention-req-badge">{categoryText}</span>
                      )}
                    </div>
                    {reasonText && (
                      <p className="attention-msg-text">{reasonText}</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Supporting Grid: ALREADY MATCHED & NEEDS VERIFICATION */}
      <div className="gap-supporting-grid">
        {/* Card 1: Already Matched */}
        <div className="supporting-card">
          <div className="supporting-header">
            <div className="supporting-title-group">
              <span className="supporting-icon icon-matched" aria-hidden="true">✓</span>
              <span className="supporting-title">ALREADY MATCHED</span>
            </div>
            <span className="supporting-count">
              {matched.length} {matched.length === 1 ? "item" : "items"}
            </span>
          </div>

          {matched.length === 0 ? (
            <p className="supporting-empty">No criteria verified as fully matched yet.</p>
          ) : (
            <ul className="supporting-list">
              {matched.map((item, idx) => {
                const reqText = item.requirement || item.item || item.label || "Requirement";
                const msgText = item.message || item.reason || "";

                return (
                  <li key={idx} className="supporting-list-item">
                    <span className="item-mark mark-matched" aria-hidden="true">✓</span>
                    <div className="item-content">
                      <span className="item-req-title">{reqText}</span>
                      {msgText && <span className="item-req-sub">{msgText}</span>}
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </div>

        {/* Card 2: Needs Verification */}
        <div className="supporting-card">
          <div className="supporting-header">
            <div className="supporting-title-group">
              <span className="supporting-icon icon-verify" aria-hidden="true">?</span>
              <span className="supporting-title">NEEDS VERIFICATION</span>
            </div>
            <span className="supporting-count">
              {needs_verification.length} {needs_verification.length === 1 ? "item" : "items"}
            </span>
          </div>

          {needs_verification.length === 0 ? (
            <p className="supporting-empty">No criteria pending verification.</p>
          ) : (
            <ul className="supporting-list">
              {needs_verification.map((item, idx) => {
                const reqText = item.requirement || item.item || item.label || "Requirement";
                const msgText = item.message || item.reason || "";

                return (
                  <li key={idx} className="supporting-list-item">
                    <span className="item-mark mark-verify" aria-hidden="true">?</span>
                    <div className="item-content">
                      <span className="item-req-title">{reqText}</span>
                      {msgText && <span className="item-req-sub">{msgText}</span>}
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </div>
    </section>
  );
}

export default GapAnalysis;
