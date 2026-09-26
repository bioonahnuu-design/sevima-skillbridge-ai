import { useState } from "react";

const OPPORTUNITY_TYPES = [
  "Scholarship",
  "Internship",
  "Exchange",
  "Competition",
  "Other",
];

function OpportunityForm({ onAnalyze, isLoading = false, error = null }) {
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
    <form className="form" onSubmit={handleSubmit}>
      <fieldset className="chip-fieldset">
        <legend>Opportunity type</legend>
        <div
          className="chip-row"
          role="radiogroup"
          aria-label="Opportunity type"
        >
          {OPPORTUNITY_TYPES.map((type) => {
            const selected = opportunityType === type;
            return (
              <button
                key={type}
                type="button"
                role="radio"
                aria-checked={selected}
                className={selected ? "chip chip-selected" : "chip"}
                onClick={() => setOpportunityType(type)}
                disabled={isLoading}
              >
                {type}
              </button>
            );
          })}
        </div>
      </fieldset>

      <div className="field">
        <label htmlFor="opportunityText">Opportunity details</label>
        <textarea
          id="opportunityText"
          name="opportunityText"
          className="opportunity-input"
          rows="10"
          placeholder="Paste the opportunity description, requirements, eligibility, deadline, benefits, or announcement here..."
          value={opportunity}
          onChange={handleTextChange}
          disabled={isLoading}
        />
      </div>

      {validationError && (
        <div className="alert alert-warning" role="alert">
          {validationError}
        </div>
      )}

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      <button
        type="submit"
        className={`analyze-button ${isLoading ? "analyze-button-loading" : ""}`}
        disabled={isLoading}
      >
        <span className="spark" aria-hidden="true">
          ✦
        </span>
        {isLoading ? "Analyzing Opportunity..." : "Analyze My Match →"}
      </button>
    </form>
  );
}

export default OpportunityForm;
