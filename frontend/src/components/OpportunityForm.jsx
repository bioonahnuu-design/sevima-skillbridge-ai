import { useState } from "react";

const OPPORTUNITY_TYPES = [
  "Scholarship",
  "Internship",
  "Exchange",
  "Competition",
  "Other",
];

function OpportunityForm({
  onAnalyze,
  isLoading = false,
  loadingStage = "",
  error = null,
}) {
  const [opportunityType, setOpportunityType] = useState("Scholarship");
  const [opportunity, setOpportunity] = useState("");
  const [validationError, setValidationError] = useState(null);

  function handleTextChange(event) {
    setOpportunity(event.target.value);
    if (validationError) {
      setValidationError(null);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    if (isLoading) return;

    if (!opportunity || !opportunity.trim()) {
      setValidationError(
        "Please paste or type an opportunity description before analyzing.",
      );
      return;
    }

    setValidationError(null);
    if (onAnalyze) {
      onAnalyze({
        opportunity_type: opportunityType,
        description: opportunity.trim(),
      });
    }
  }

  return (
    <form className="workspace-form form" onSubmit={handleSubmit}>
      {/* Opportunity Type Selector */}
      <fieldset className="chip-fieldset form-group field">
        <legend className="form-label" id="opp-type-label">
          <span>Opportunity Type</span>
          <span className="form-hint">Pilih jenis program</span>
        </legend>
        <div
          className="type-chip-row chip-row"
          role="radiogroup"
          aria-labelledby="opp-type-label"
        >
          {OPPORTUNITY_TYPES.map((type) => {
            const selected = opportunityType === type;
            return (
              <button
                key={type}
                type="button"
                role="radio"
                aria-checked={selected}
                className={`type-chip chip ${selected ? "type-chip-active chip-selected" : ""}`}
                onClick={() => setOpportunityType(type)}
                disabled={isLoading}
              >
                {selected && (
                  <span className="type-chip-check" aria-hidden="true">
                    ✓
                  </span>
                )}
                <span>{type}</span>
              </button>
            );
          })}
        </div>
      </fieldset>

      {/* Opportunity Details Textarea */}
      <div className="form-group field">
        <label htmlFor="opportunityText" className="form-label">
          <span>Opportunity Details</span>
          <span className="form-hint">Detail &amp; Persyaratan</span>
        </label>
        <textarea
          id="opportunityText"
          name="opportunityText"
          className="form-textarea opportunity-textarea opportunity-input"
          rows="9"
          placeholder="Paste the opportunity description, requirements, eligibility, deadline, benefits, or announcement here..."
          value={opportunity}
          onChange={handleTextChange}
          disabled={isLoading}
        />
        <div className="textarea-footer">
          <span className="textarea-tip">
            Tip: Sertakan persyaratan IPK, semester, keahlian, dan batas pendaftaran jika tersedia.
          </span>
          <span className="char-count">{opportunity.length} chars</span>
        </div>
      </div>

      {/* Validation or API Error Alerts */}
      {validationError && (
        <div className="alert-banner alert alert-warning" role="alert">
          <span className="alert-icon" aria-hidden="true">⚠</span>
          <span>{validationError}</span>
        </div>
      )}

      {error && (
        <div className="alert-banner alert alert-error" role="alert">
          <span className="alert-icon" aria-hidden="true">⚠</span>
          <span>{error}</span>
        </div>
      )}

      {/* Dominant Action Button */}
      <button
        type="submit"
        className={`dominant-action-btn analyze-button ${isLoading ? "analyze-button-loading" : ""}`}
        disabled={isLoading}
      >
        {isLoading ? (
          <>
            <span className="btn-spinner" aria-hidden="true" />
            <span>{loadingStage || "Analyzing Opportunity..."}</span>
          </>
        ) : (
          <>
            <span>Analyze My Match</span>
            <span className="btn-arrow" aria-hidden="true">
              →
            </span>
          </>
        )}
      </button>
    </form>
  );
}

export default OpportunityForm;
