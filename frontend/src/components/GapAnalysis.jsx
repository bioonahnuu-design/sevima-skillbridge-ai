function GapAnalysis({ data }) {
  if (!data) return null;

  const {
    gaps = [],
    matched = [],
    needs_verification = [],
  } = data;

  return (
    <section className="gap-report-container" aria-labelledby="gap-report-heading">
      {/* Section Header */}
      <div className="gap-report-header">
        <span className="gap-eyebrow">GAP ANALYSIS</span>
        <h2 id="gap-report-heading" className="gap-title">
          What&apos;s holding you back?
        </h2>
        <p className="gap-subtitle">
          Focus on the requirements that need attention before you apply.
        </p>
      </div>

      {/* Dominant Block: NEEDS ATTENTION */}
      <div className="needs-attention-block">
        <div className="attention-header-bar">
          <div className="attention-tag-group">
            <span className="attention-bullet" aria-hidden="true">!</span>
            <span className="attention-label">NEEDS ATTENTION</span>
          </div>
          <span className="attention-count-tag">
            {gaps.length} item{gaps.length === 1 ? "" : "s"} need attention
          </span>
        </div>

        {gaps.length > 0 ? (
          <div className="attention-items-stack">
            {gaps.map((item, idx) => {
              const numStr = String(idx + 1).padStart(2, "0");
              return (
                <div key={idx} className="attention-row">
                  <div className="attention-num-col">
                    <span className="attention-num">{numStr}</span>
                  </div>
                  <div className="attention-body-col">
                    <div className="attention-req-row">
                      <span className="attention-req-name">{item.requirement}</span>
                      <span className="attention-req-badge">
                        Required by this opportunity
                      </span>
                    </div>
                    <p className="attention-msg-text">
                      {item.message || "No supporting evidence found in your profile."}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="attention-empty-state">
            <span className="empty-check-icon" aria-hidden="true">✓</span>
            <div>
              <p className="empty-strong">No blocking gaps detected!</p>
              <p className="empty-sub">
                Your profile satisfies the stated criteria for this opportunity.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Supporting Sections: ALREADY MATCHED & NEEDS VERIFICATION */}
      <div className="gap-supporting-grid">
        {/* Already Matched */}
        <div className="supporting-card matched-card">
          <div className="supporting-header">
            <div className="supporting-title-group">
              <span className="supporting-icon icon-matched" aria-hidden="true">✓</span>
              <h3 className="supporting-title">ALREADY MATCHED</h3>
            </div>
            <span className="supporting-count">{matched.length} satisfied</span>
          </div>

          {matched.length > 0 ? (
            <ul className="supporting-list">
              {matched.map((item, idx) => (
                <li key={idx} className="supporting-list-item">
                  <span className="item-mark mark-matched" aria-hidden="true">✓</span>
                  <div className="item-content">
                    <span className="item-req-title">{item.requirement}</span>
                    {item.message && (
                      <span className="item-req-sub">{item.message}</span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="supporting-empty">No criteria evaluated as matched yet.</p>
          )}
        </div>

        {/* Needs Verification */}
        <div className="supporting-card verify-card">
          <div className="supporting-header">
            <div className="supporting-title-group">
              <span className="supporting-icon icon-verify" aria-hidden="true">?</span>
              <h3 className="supporting-title">NEEDS VERIFICATION</h3>
            </div>
            <span className="supporting-count">{needs_verification.length} items</span>
          </div>

          {needs_verification.length > 0 ? (
            <ul className="supporting-list">
              {needs_verification.map((item, idx) => (
                <li key={idx} className="supporting-list-item">
                  <span className="item-mark mark-verify" aria-hidden="true">?</span>
                  <div className="item-content">
                    <span className="item-req-title">{item.requirement}</span>
                    {item.message && (
                      <span className="item-req-sub">{item.message}</span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="supporting-empty">
              No extra verification items detected in opportunity text.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}

export default GapAnalysis;
