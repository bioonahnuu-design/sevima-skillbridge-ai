import { useState } from "react";
import Navbar from "../components/Navbar.jsx";
import ProfileForm from "../components/ProfileForm.jsx";
import OpportunityForm from "../components/OpportunityForm.jsx";
import OpportunityAnalysis from "../components/OpportunityAnalysis.jsx";
import ProfileMatch from "../components/ProfileMatch.jsx";
import { analyzeOpportunity, matchProfile } from "../services/api.js";

function Dashboard() {
  const [profile, setProfile] = useState({
    studyProgram: "",
    semester: "",
    gpa: "",
    skills: "",
    experience: "",
  });

  const [analysisData, setAnalysisData] = useState(null);
  const [matchData, setMatchData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  function handleProfileChange(name, value) {
    setProfile((prev) => ({ ...prev, [name]: value }));
  }

  async function handleAnalyze({ opportunity_type, description }) {
    setIsLoading(true);
    setError(null);

    // Profile validation
    if (profile.gpa && profile.gpa.trim()) {
      const parsedGpa = parseFloat(profile.gpa.replace(",", "."));
      if (isNaN(parsedGpa) || parsedGpa < 0 || parsedGpa > 4.0) {
        setError("Please enter a valid GPA between 0.00 and 4.00.");
        setIsLoading(false);
        return;
      }
    }

    if (profile.semester && profile.semester.trim()) {
      const parsedSem = parseInt(profile.semester, 10);
      if (isNaN(parsedSem) || parsedSem < 1 || parsedSem > 14) {
        setError("Please enter a valid semester number (1 to 14).");
        setIsLoading(false);
        return;
      }
    }

    const formattedProfile = {
      study_program: profile.studyProgram ? profile.studyProgram.trim() : "",
      semester:
        profile.semester && profile.semester.trim()
          ? parseInt(profile.semester, 10)
          : null,
      gpa:
        profile.gpa && profile.gpa.trim()
          ? parseFloat(profile.gpa.replace(",", "."))
          : null,
      skills: profile.skills
        ? profile.skills
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean)
        : [],
      experience: profile.experience ? profile.experience.trim() : "",
    };

    try {
      // 1. Analyze Opportunity
      const oppResult = await analyzeOpportunity({
        opportunity_type,
        description,
      });
      setAnalysisData(oppResult);

      // 2. Perform Profile Match & Gap Analysis
      const matchResult = await matchProfile({
        profile: formattedProfile,
        opportunity: oppResult,
      });
      setMatchData(matchResult);
    } catch (err) {
      setError(
        err.message ||
          "Failed to process match analysis. Please check if the backend is running at http://localhost:8000.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <Navbar />

      <main className="page">
        <section className="hero" aria-labelledby="hero-heading">
          <p className="hero-pill">YOUR AI OPPORTUNITY COPILOT</p>
          <h1 id="hero-heading" className="hero-title">
            Turn opportunities into
            <span className="hero-highlight"> your next move.</span>
          </h1>
          <p className="hero-copy">
            Analyze scholarships, internships, exchanges and other opportunities
            against your profile — then discover your gaps and the actions that
            matter most.
          </p>
          <ul className="hero-benefits">
            <li>
              <span className="benefit-check" aria-hidden="true">
                ✓
              </span>
              Profile Match
            </li>
            <li>
              <span className="benefit-check" aria-hidden="true">
                ✓
              </span>
              Gap Analysis
            </li>
            <li>
              <span className="benefit-check" aria-hidden="true">
                ✓
              </span>
              Action Plan
            </li>
          </ul>
        </section>

        <ol className="journey" aria-label="How SkillBridge works">
          <li>Profile</li>
          <li>Opportunity</li>
          <li>AI Match</li>
          <li>Action</li>
        </ol>

        <section className="workspace" aria-label="SkillBridge workspace">
          <article className="card">
            <header className="card-header">
              <div className="card-icon" aria-hidden="true">
                <span className="student-icon">👤</span>
              </div>
              <div>
                <p className="step-label">STEP 01</p>
                <h2>Build Your Profile</h2>
                <p className="card-subtitle">
                  Tell SkillBridge about your background so your opportunities
                  can be evaluated personally.
                </p>
              </div>
            </header>
            <ProfileForm profile={profile} onChange={handleProfileChange} />
          </article>

          <article className="card">
            <header className="card-header">
              <div className="card-icon card-icon-spark" aria-hidden="true">
                <span className="spark">✦</span>
              </div>
              <div>
                <p className="step-label">STEP 02</p>
                <h2>Analyze an Opportunity</h2>
                <p className="card-subtitle">
                  Paste an opportunity and let SkillBridge understand its
                  requirements.
                </p>
              </div>
            </header>
            <OpportunityForm
              onAnalyze={handleAnalyze}
              isLoading={isLoading}
              error={error}
            />
          </article>
        </section>

        {/* Core Feature #1: Structured Opportunity Analysis */}
        {analysisData && <OpportunityAnalysis data={analysisData} />}

        {/* Core Feature #2: Profile Match Score & Gap Analysis */}
        {matchData && <ProfileMatch data={matchData} />}
      </main>
    </div>
  );
}

export default Dashboard;
