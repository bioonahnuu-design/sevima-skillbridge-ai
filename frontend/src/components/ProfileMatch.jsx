import { useState, useEffect } from "react";

function formatStatusBadge(status) {
  switch (status) {
    case "matched":
      return { label: "MATCHED", className: "status-pill status-matched" };
    case "partial":
      return { label: "PARTIAL", className: "status-pill status-partial" };
    case "missing":
      return { label: "MISSING", className: "status-pill status-missing" };
    case "needs_verification":
      return {
        label: "VERIFY",
        className: "status-pill status-verify",
      };
    case "upcoming":
      return { label: "UPCOMING", className: "status-pill status-upcoming" };
    case "today":
      return { label: "TODAY", className: "status-pill status-today" };
    case "passed":
      return { label: "PASSED", className: "status-pill status-passed" };
    case "not_specified":
    default:
      return {
        label: "NOT SPECIFIED",
        className: "status-pill status-unspecified",
      };
  }
}

function useAnimatedScore(targetScore, duration = 850) {
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    const prefersReducedMotion =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (prefersReducedMotion) {
      setDisplayScore(targetScore);
      return;
    }

    let startTimestamp = null;
    let animationFrameId;

    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const eased = 1 - (1 - progress) * (1 - progress);
      setDisplayScore(Math.round(eased * targetScore));

      if (progress < 1) {
        animationFrameId = window.requestAnimationFrame(step);
      }
    };

    animationFrameId = window.requestAnimationFrame(step);
    return () => window.cancelAnimationFrame(animationFrameId);
  }, [targetScore, duration]);

  return displayScore;
}

function ProfileMatch({ data }) {
  if (!data) return null;

  const {
    match_score = 0,
    summary = "",
    breakdown = {},
  } = data;

  const animatedScore = useAnimatedScore(match_score);

  const categories = [
    { key: "academic", title: "Academic Fit", weight: 20 },
    { key: "eligibility", title: "Eligibility", weight: 40 },
    { key: "skills", title: "Skills Fit", weight: 15 },
    { key: "documents", title: "Document Readiness", weight: 15 },
    { key: "deadline", title: "Deadline Readiness", weight: 10 },
  ];

  const alignmentLabel =
    match_score >= 80
      ? "Strong Profile Alignment"
      : match_score >= 60
        ? "Moderate Profile Alignment"
        : "Needs Preparation";

  const alignmentDesc =
    match_score >= 80
      ? "You satisfy most core requirements across academic benchmarks and prerequisites."
      : match_score >= 60
        ? "Moderate compatibility. Focus on bridging the identified requirement gaps."
        : "Several core prerequisites require preparation before submission.";

  return (
    <section className="profile-readiness-hero" aria-labelledby="readiness-hero-title">
      {/* Eyebrow */}
      <div className="readiness-header-row">
        <span className="readiness-eyebrow">PROFILE READINESS</span>
        <span className="readiness-stamp">{alignmentLabel}</span>
      </div>

      {/* Hero Score Showcase */}
      <div className="readiness-showcase">
        <div className="readiness-score-display">
          <div className="readiness-score-number">
            <span className="score-val">{animatedScore}</span>
            <span className="score-denom">/ 100</span>
          </div>
          <span className="readiness-score-tag">PROFILE MATCH</span>
        </div>

        <div className="readiness-narrative">
          <h3 id="readiness-hero-title" className="readiness-headline">
            {alignmentLabel}
          </h3>
          <p className="readiness-summary-desc">
            {summary || alignmentDesc}
          </p>

          <div className="readiness-disclaimer" role="note">
            <span className="disclaimer-icon" aria-hidden="true">ℹ</span>
            <span>
              <strong>Note:</strong> Profile Match Score evaluates compatibility and readiness based on stated criteria. It does not represent or guarantee selection or scholarship acceptance probability.
            </span>
          </div>
        </div>
      </div>

      {/* Breakdown Dimension Rows with Clean Tracks */}
      <div className="readiness-breakdown-panel">
        <div className="breakdown-intro-row">
          <span className="breakdown-label">EVALUATION BREAKDOWN</span>
          <span className="breakdown-weight-label">Weighted Total: 100%</span>
        </div>

        <div className="breakdown-rows-stack">
          {categories.map(({ key, title, weight }) => {
            const catData = breakdown[key] || {
              status: "not_specified",
              score: 0,
              detail: "Not evaluated",
            };
            const badge = formatStatusBadge(catData.status);
            const scoreVal =
              typeof catData.score === "number" ? Math.round(catData.score) : 0;
            const percentage =
              weight > 0 ? Math.min(100, Math.round((scoreVal / weight) * 100)) : 0;

            return (
              <div key={key} className="breakdown-row-item">
                <div className="breakdown-row-info">
                  <div className="breakdown-name-wrap">
                    <span className="breakdown-dim-title">{title}</span>
                    <span className="breakdown-weight-tag">({weight}%)</span>
                  </div>

                  <div className="breakdown-status-wrap">
                    <span className={badge.className}>{badge.label}</span>
                    <span className="breakdown-pts">
                      {scoreVal} / {weight} pts
                    </span>
                  </div>
                </div>

                {/* Progress Bar Track */}
                <div className="breakdown-bar-track" aria-hidden="true">
                  <div
                    className={`breakdown-bar-fill ${percentage > 0 ? "fill-active" : "fill-empty"}`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>

                {catData.detail && (
                  <p className="breakdown-detail-text">{catData.detail}</p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

export default ProfileMatch;
