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
    setCompletedPriorities((prev) => {
      const nextVal = !prev[index];
      const updated = { ...prev, [index]: nextVal };
      if (index === 0) {
        updated["spotlight"] = nextVal;
      }
      return updated;
    });
  }

  function toggleSpotlight() {
    setCompletedPriorities((prev) => {
      const nextVal = !prev["spotlight"];
      const updated = { ...prev, spotlight: nextVal };
      if (priority_actions.length > 0) {
        updated[0] = nextVal;
      }
      return updated;
    });
  }

  function toggleVerification(index) {
    setCompletedVerifications((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  }

  const spotlightReason =
    priority_actions[0]?.reason ||
    "Immediate high-leverage focus area to address your most critical requirement gap.";
  const spotlightPriority = priority_actions[0]?.priority || "High";
  const isSpotlightDone = Boolean(completedPriorities["spotlight"]);

  return (
    <section
      className="action-roadmap-section"
      aria-labelledby="action-plan-title"
    >
      {/* 1. Header */}
      <div className="action-plan-header">
        <div className="action-plan-eyebrow-row">
          <span className="action-plan-eyebrow">ACTION PLAN</span>
          {deadline_status && (
            <span className="roadmap-deadline-pill">
              <span className="deadline-clock-icon" aria-hidden="true">
                ⏱
              </span>
              <span>{deadline_status}</span>
            </span>
          )}
        </div>
        <h2 id="action-plan-title" className="action-plan-title">
          Turn your gaps into progress.
        </h2>
        <p className="action-plan-subtitle">
          Concrete, prioritized steps and verification items tailored to bridge your readiness gaps.
        </p>
        {summary && <p className="action-plan-summary-note">{summary}</p>}
      </div>

      {/* 2. NEXT BEST ACTION Spotlight Card */}
      {next_best_action && (
        <div className="next-best-spotlight">
          <div className="spotlight-top-bar">
            <span className="spotlight-tag">
              <span aria-hidden="true">✦</span> NEXT BEST ACTION
            </span>
            <span className="spotlight-step-num">STEP 01</span>
          </div>

          <div className="spotlight-action-text">
            {next_best_action}
          </div>

          {spotlightReason && (
            <p className="spotlight-reason-text">
              {spotlightReason}
            </p>
          )}

          <div className="spotlight-footer">
            <span className="spotlight-priority-badge">
              {(spotlightPriority || "HIGH").toUpperCase()} PRIORITY
            </span>
            <button
              type="button"
              className={`spotlight-toggle-btn ${isSpotlightDone ? "btn-marked-done" : ""}`}
              onClick={toggleSpotlight}
            >
              <span aria-hidden="true">{isSpotlightDone ? "✓" : "○"}</span>
              <span>{isSpotlightDone ? "Completed" : "Mark as Done"}</span>
            </button>
          </div>
        </div>
      )}

      {/* 3. YOUR ROADMAP */}
      <div className="roadmap-container">
        <div className="roadmap-header-row">
          <h3 className="roadmap-title">YOUR ROADMAP</h3>
          <span className="roadmap-count-pill">
            {priority_actions.length} {priority_actions.length === 1 ? "Action" : "Actions"}
          </span>
        </div>

        {priority_actions.length > 0 ? (
          <div className="vertical-timeline-stack">
            {priority_actions.map((item, idx) => {
              const isDone = Boolean(completedPriorities[idx]);
              const stageLabel = idx === 0 ? "NOW" : idx === 1 ? "NEXT" : "THEN";
              const prioClass = `prio-tag prio-${(item.priority || "medium").toLowerCase()}`;

              return (
                <div
                  key={idx}
                  className={`timeline-roadmap-item ${isDone ? "item-is-done" : ""}`}
                >
                  <div className="timeline-node-col">
                    <button
                      type="button"
                      className="node-check-btn"
                      title={isDone ? "Mark as incomplete" : "Mark as completed"}
                      aria-label={`Mark step ${idx + 1} as ${isDone ? "incomplete" : "completed"}`}
                      onClick={() => togglePriority(idx)}
                    >
                      <span
                        className={`node-marker ${isDone ? "marker-done" : "marker-active"}`}
                      >
                        {isDone ? "✓" : idx + 1}
                      </span>
                    </button>
                    <div className="timeline-vertical-wire" aria-hidden="true" />
                  </div>

                  <div className="timeline-content-col">
                    <div className="timeline-stage-row">
                      <span className="stage-name-pill">{stageLabel}</span>
                      <span className={prioClass}>
                        {(item.priority || "Medium").toUpperCase()}
                      </span>
                      {item.category && (
                        <span className="req-name-tag">• {item.category}</span>
                      )}
                      {item.requirement && (
                        <span className="req-name-tag">({item.requirement})</span>
                      )}
                    </div>

                    <div className="timeline-action-statement">
                      {item.action}
                    </div>

                    {item.reason && (
                      <p className="timeline-reason-text">
                        <span className="reason-label">Mengapa:</span> {item.reason}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Terminal Milestone Node */}
            <div className="timeline-roadmap-item">
              <div className="timeline-node-col">
                <span className="node-marker marker-terminal" aria-hidden="true">
                  ★
                </span>
              </div>
              <div className="timeline-content-col">
                <div className="timeline-stage-row">
                  <span className="stage-name-pill stage-terminal">FINAL</span>
                </div>
                <div className="terminal-title">Ready to Submit Application</div>
                <p className="terminal-desc">
                  Once all milestone actions and verifications are completed, submit your application.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="roadmap-ready-state">
            <div className="ready-state-badge">
              <span className="ready-state-check" aria-hidden="true">✓</span>
              <span className="ready-state-pill">PROFILE READY</span>
            </div>
            <h4 className="ready-state-title">No Urgent Action Gaps Detected</h4>
            <p className="ready-state-desc">
              Your student profile satisfies all major explicit criteria. Review the verification checklist below to ensure all official documents and administrative criteria are in order.
            </p>
            {summary && <p className="ready-summary-quote">"{summary}"</p>}
            <div className="terminal-ready-box">
              <span aria-hidden="true">🚀</span>
              <span>You are in strong alignment to proceed directly with your application.</span>
            </div>
          </div>
        )}
      </div>

      {/* 4. Verification Checklist */}
      {verification_actions.length > 0 && (
        <div className="verification-checklist-panel">
          <div className="checklist-header-row">
            <div>
              <h3 className="checklist-title">Verification Checklist</h3>
              <p className="checklist-subtitle">
                Confirm these requirements before final submission
              </p>
            </div>
            <span className="checklist-count-tag">
              {verification_actions.length}{" "}
              {verification_actions.length === 1 ? "Item" : "Items"}
            </span>
          </div>

          <div className="checklist-items-grid">
            {verification_actions.map((item, idx) => {
              const isDone = Boolean(completedVerifications[idx]);

              return (
                <div
                  key={idx}
                  className={`verification-check-row ${isDone ? "check-row-done" : ""}`}
                  onClick={() => toggleVerification(idx)}
                  style={{ cursor: "pointer" }}
                >
                  <button
                    type="button"
                    className="verification-toggle-box"
                    aria-label={`Mark ${item.requirement} as ${isDone ? "unverified" : "verified"}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleVerification(idx);
                    }}
                  >
                    <span
                      className={`custom-checkbox ${isDone ? "box-checked" : ""}`}
                    >
                      {isDone && <span className="check-mark">✓</span>}
                    </span>
                  </button>

                  <div className="verification-text-wrap">
                    <span className="verification-req-name">
                      {item.requirement}
                    </span>
                    <span className="verification-action-desc">
                      {item.action}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </section>
  );
}

export default ActionPlan;
