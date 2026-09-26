const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Sends an opportunity to the backend analyzer.
 * @param {Object} payload
 * @param {string} payload.opportunity_type - e.g. "Scholarship", "Internship", "Exchange"
 * @param {string} payload.description - Opportunity details / raw text
 * @returns {Promise<{opportunity_type: string, analysis: Object}>} Analysis result
 */
export async function analyzeOpportunity({ opportunity_type, description }) {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      opportunity_type,
      description,
    }),
  });

  if (!response.ok) {
    let errorMessage = `Analysis request failed with status ${response.status}`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        if (typeof errorJson.detail === "string") {
          errorMessage = errorJson.detail;
        } else if (
          Array.isArray(errorJson.detail) &&
          errorJson.detail[0]?.msg
        ) {
          errorMessage = errorJson.detail[0].msg;
        }
      }
    } catch {
      if (response.statusText) {
        errorMessage = response.statusText;
      }
    }
    throw new Error(errorMessage);
  }

  return await response.json();
}

/**
 * Evaluates profile match and gaps against analyzed opportunity.
 * @param {Object} payload
 * @param {Object} payload.profile - Student profile data
 * @param {Object} payload.opportunity - The OpportunityAnalyzeResponse object
 * @returns {Promise<Object>} Match result
 */
export async function matchProfile({ profile, opportunity }) {
  const response = await fetch(`${API_BASE_URL}/api/match`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      profile,
      opportunity,
    }),
  });

  if (!response.ok) {
    let errorMessage = `Matching request failed with status ${response.status}`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        if (typeof errorJson.detail === "string") {
          errorMessage = errorJson.detail;
        } else if (
          Array.isArray(errorJson.detail) &&
          errorJson.detail[0]?.msg
        ) {
          errorMessage = errorJson.detail[0].msg;
        }
      }
    } catch {
      if (response.statusText) {
        errorMessage = response.statusText;
      }
    }
    throw new Error(errorMessage);
  }

  return await response.json();
}
