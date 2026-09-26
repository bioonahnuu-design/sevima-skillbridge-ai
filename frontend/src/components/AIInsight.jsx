function AIInsight({ personalization, isAvailable = true }) {
  const hasContent = Boolean(isAvailable && personalization);

  if (!hasContent) {
    return (
      <section
        className="ai-insight-panel ai-insight-fallback"
        aria-labelledby="ai-insight-title"
      >
        <div className="ai-insight-header">
          <div className="ai-insight-badge-row">
            <span className="ai-insight-eyebrow">AI-GUIDED INSIGHT</span>
            <span className="ai-insight-stamp ai-stamp-muted">Notice</span>
          </div>
          <h3 id="ai-insight-title" className="ai-insight-title">
            Personalized Strategy
          </h3>
        </div>
        <div className="ai-fallback-content">
          <p className="ai-fallback-message">
            AI personalization is currently unavailable. Your deterministic
            evaluation and action plan remain available.
          </p>
        </div>
      </section>
    );
  }

  const {
    summary = "",
    why_this_match = "",
    focus_areas = [],
    recommended_strategy = "",
    encouragement = "",
  } = personalization;

  const focusFirst =
    focus_areas && focus_areas.length > 0 ? focus_areas[0] : null;
  const subsequentFocus =
    focus_areas && focus_areas.length > 1 ? focus_areas.slice(1) : [];

  return (
    <section className="ai-insight-panel" aria-labelledby="ai-insight-title">
      <div className="ai-insight-header">
        <div className="ai-insight-badge-row">
          <span className="ai-insight-eyebrow">AI-GUIDED INSIGHT</span>
          <span className="ai-insight-stamp">Personalized Strategy</span>
        </div>
        <h3 id="ai-insight-title" className="ai-insight-title">
          Personalized Strategy
        </h3>
        {summary && <p className="ai-insight-summary">{summary}</p>}
      </div>

      <div className="ai-insight-content-grid">
        {focusFirst && (
          <div className="ai-insight-block">
            <h4 className="ai-insight-block-title">FOCUS FIRST</h4>
            <p className="ai-insight-text">{focusFirst}</p>
          </div>
        )}

        {subsequentFocus.length > 0 && (
          <div className="ai-insight-block">
            <h4 className="ai-insight-block-title">THEN</h4>
            <p className="ai-insight-text">{subsequentFocus.join("; ")}</p>
          </div>
        )}

        {why_this_match && (
          <div className="ai-insight-block">
            <h4 className="ai-insight-block-title">WHY</h4>
            <p className="ai-insight-text">{why_this_match}</p>
          </div>
        )}

        {recommended_strategy && (
          <div className="ai-insight-block">
            <h4 className="ai-insight-block-title">RECOMMENDED STRATEGY</h4>
            <p className="ai-insight-text">{recommended_strategy}</p>
          </div>
        )}
      </div>

      {focus_areas && focus_areas.length > 0 && (
        <div className="ai-focus-areas-row">
          <span className="ai-focus-label">FOCUS AREAS:</span>
          <div className="ai-focus-tags">
            {focus_areas.map((area, idx) => (
              <span key={idx} className="ai-focus-pill">
                {area}
              </span>
            ))}
          </div>
        </div>
      )}

      {encouragement && (
        <div className="ai-encouragement-row">
          <span className="encouragement-icon" aria-hidden="true">
            💡
          </span>
          <p className="encouragement-text">{encouragement}</p>
        </div>
      )}
    </section>
  );
}

export default AIInsight;
