import { useState } from "react";

function ActionPlan({ data }) {
  if (!data) return null;

  const {
    summary = "",
    priority_actions = [],
    verification_actions = [],
    deadline_status = "",
    next_best_action = "",
  } = data;

  const [completedPriorities, setCompletedPriorities] = useState({});
  const [completedVerifications, setCompletedVerifications] = useState({});

  function togglePriority(index) {
    setCompletedPriorities((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  }

  function toggleVerification(index) {
    setCompletedVerifications((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  }

  // Determine stage label for vertical roadmap
  function getStageLabel(idx) {
    if (idx === 0) return "NOW";
    if (idx === 1) return "NEXT";
    return "THEN";
  }

  return (
    <section className="action-roadmap-section" aria-labelledby="action-plan-heading">
      {/* 13. Section Header */}
      <div className="action-plan-header">
        <div className="action-plan-eyebrow-row">
          <span className="action-plan-eyebrow">ACTION PLAN</span>
          {deadline_status && (
            <span className="roadmap-deadline-pill">
              <span className="deadline-clock-icon" aria-hidden="true">⏱</span>
              <span>DEADLINE: {deadline_status}</span>
            </span>
          )}
        </div>
        <h2 id="action-plan-heading" className="action-plan-title">
          Turn your gaps into progress.
        </h2>
        <p className="action-plan-subtitle">
          A prioritized roadmap based on what your opportunity requires.
        </p>
        {summary && <p className="action-plan-summary-note">{summary}</p>}
      </div>

      {/* 14. NEXT BEST ACTION Spotlight */}
      {next_best_action && (
        <div className="next-best-spotlight">
          <div className="spotlight-top-bar">
            <span className="spotlight-tag">
              <span className="spotlight-spark" aria-hidden="true">✦</span>
              <span>NEXT BEST ACTION</span>
            </span>
            <span className="spotlight-step-num">01</span>
          </div>

          <div className="spotlight-body">
            <h3 className="spotlight-action-text">{next_best_action}</h3>
            {priority_actions[0]?.reason && (
              <p className="spotlight-reason-text">
                {priority_actions[0].reason}
              </p>
            )}
          </div>

          <div className="spotlight-footer">
            <span className="spotlight-priority-badge">
              {priority_actions[0]?.priority || "HIGH"} PRIORITY
            </span>
            <button
              type="button"
              className={`spotlight-toggle-btn ${completedPriorities[0] ? "btn-marked-done" : ""}`}
              onClick={() => togglePriority(0)}
            >
              <span className="btn-check-icon" aria-hidden="true">
                {completedPriorities[0] ? "✓" : "○"}
              </span>
              <span>{completedPriorities[0] ? "Completed" : "Mark as Done"}</span>
            </button>
          </div>
        </div>
      )}

      {/* 15. ACTION ROADMAP (Vertical Timeline) */}
      <div className="roadmap-container">
        <div className="roadmap-header-row">
          <h3 className="roadmap-title">YOUR ROADMAP</h3>
          <span className="roadmap-count-pill">
            {priority_actions.length} prioritized step{priority_actions.length === 1 ? "" : "s"}
          </span>
        </div>

        {priority_actions.length > 0 ? (
          <div className="vertical-timeline-stack">
            {priority_actions.map((item, idx) => {
              const isDone = Boolean(completedPriorities[idx]);
              const stageLabel = getStageLabel(idx);
              const prioClass = `prio-tag prio-${item.priority.toLowerCase()}`;

              return (
                <div
                  key={idx}
                  className={`timeline-roadmap-item ${isDone ? "item-is-done" : ""}`}
                >
                  {/* Timeline Left Node */}
                  <div className="timeline-node-col">
                    <button
                      type="button"
                      className="node-check-btn"
                      aria-label={`Mark step ${item.requirement} as ${isDone ? "incomplete" : "completed"}`}
                      onClick={() => togglePriority(idx)}
                    >
                      <span className={`node-marker ${isDone ? "marker-done" : "marker-active"}`}>
                        {isDone ? "✓" : "●"}
                      </span>
                    </button>
                    {/* Connecting vertical line (unless last node) */}
                    <div className="timeline-vertical-wire" aria-hidden="true" />
                  </div>

                  {/* Timeline Right Content */}
                  <div className="timeline-content-col">
                    <div className="timeline-stage-row">
                      <span className="stage-name-pill">{stageLabel}</span>
                      <span className={prioClass}>{item.priority} PRIORITY</span>
                      <span className="req-name-tag">{item.requirement}</span>
                    </div>

                    <h4 className="timeline-action-statement">{item.action}</h4>

                    {item.reason && (
                      <p className="timeline-reason-text">
                        <span className="reason-label">Mengapa:</span> {item.reason}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}

            {/* 18. Terminal Milestone: READY TO APPLY */}
            <div className="timeline-roadmap-item terminal-milestone-item">
              <div className="timeline-node-col">
                <span className="node-marker marker-terminal">○</span>
              </div>
              <div className="timeline-content-col">
                <div className="timeline-stage-row">
                  <span className="stage-name-pill stage-terminal">GOAL</span>
                  <span className="terminal-title">READY TO APPLY</span>
                </div>
                <p className="terminal-desc">
                  Finalize your submissions with verified requirements and submitted documentation.
                </p>
              </div>
            </div>
          </div>
        ) : (
          /* 18. Ready State when no priority gap actions exist */
          <div className="roadmap-ready-state">
            <div className="ready-state-badge">
              <span className="ready-state-check" aria-hidden="true">✓</span>
              <span className="ready-state-pill">READY FOR FINAL REVIEW</span>
            </div>
            <h4 className="ready-state-title">
              Your core requirements are aligned.
            </h4>
            <p className="ready-state-desc">
              No critical prerequisite gaps detected. Complete the remaining verification checklist before submitting your application.
            </p>
            {summary && (
              <p className="ready-summary-quote">&ldquo;{summary}&rdquo;</p>
            )}

            {/* Terminal Milestone Node */}
            <div className="terminal-ready-box">
              <span className="ready-circle" aria-hidden="true">○</span>
              <div>
                <strong>READY TO APPLY</strong>
                <p>Prepare final document verification and submit before deadline.</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 16. VERIFICATION CHECKLIST (BEFORE YOU APPLY) */}
      <div className="verification-checklist-panel">
        <div className="checklist-header-row">
          <div>
            <h3 className="checklist-title">BEFORE YOU APPLY</h3>
            <p className="checklist-subtitle">
              Verify administrative prerequisites and confirm submission documents.
            </p>
          </div>
          <span className="checklist-count-tag">
            {verification_actions.length} item{verification_actions.length === 1 ? "" : "s"}
          </span>
        </div>

        {verification_actions.length > 0 ? (
          <div className="checklist-items-grid">
            {verification_actions.map((item, idx) => {
              const isDone = Boolean(completedVerifications[idx]);

              return (
                <div
                  key={idx}
                  className={`verification-check-row ${isDone ? "check-row-done" : ""}`}
                >
                  <button
                    type="button"
                    className="verification-toggle-box"
                    aria-label={`Mark verification for ${item.requirement} as ${isDone ? "incomplete" : "verified"}`}
                    onClick={() => toggleVerification(idx)}
                  >
                    <span className={`custom-checkbox ${isDone ? "box-checked" : ""}`}>
                      {isDone && <span className="check-mark">✓</span>}
                    </span>
                  </button>

                  <div className="verification-text-wrap">
                    <span className="verification-req-name">{item.requirement}</span>
                    <p className="verification-action-desc">{item.action}</p>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="verification-empty-box">
            <span className="empty-check" aria-hidden="true">✓</span>
            <p>No additional verification items detected.</p>
          </div>
        )}
      </div>
    </section>
  );
}

export default ActionPlan;
