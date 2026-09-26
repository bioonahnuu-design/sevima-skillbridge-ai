import { useState } from "react";

const OPPORTUNITY_TYPES = [
  "Scholarship",
  "Internship",
  "Exchange",
  "Competition",
  "Other",
];

function OpportunityForm() {
  const [opportunityType, setOpportunityType] = useState("Scholarship");
  const [opportunity, setOpportunity] = useState("");

  return (
    <form className="form" onSubmit={(event) => event.preventDefault()}>
      <fieldset className="chip-fieldset">
        <legend>Opportunity type</legend>
        <div className="chip-row" role="radiogroup" aria-label="Opportunity type">
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
          onChange={(event) => setOpportunity(event.target.value)}
        />
      </div>

      <button type="button" className="analyze-button">
        <span className="spark" aria-hidden="true">
          ✦
        </span>
        Analyze My Match →
      </button>
    </form>
  );
}

export default OpportunityForm;
