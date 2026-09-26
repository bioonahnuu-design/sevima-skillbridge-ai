import { useState, useEffect } from "react";
import Navbar from "../components/Navbar.jsx";
import ProfileForm from "../components/ProfileForm.jsx";
import OpportunityForm from "../components/OpportunityForm.jsx";
import OpportunityAnalysis from "../components/OpportunityAnalysis.jsx";
import ProfileMatch from "../components/ProfileMatch.jsx";
import AIInsight from "../components/AIInsight.jsx";
import GapAnalysis from "../components/GapAnalysis.jsx";
import ActionPlan from "../components/ActionPlan.jsx";
import {
  analyzeOpportunity,
  matchProfile,
  generateActionPlan,
  analyzeWithAgent,
} from "../services/api.js";
import heroIllustration from "../assets/skillbridge-hero.png";

const MARQUEE_ITEMS = [
  "SCHOLARSHIP",
  "INTERNSHIP",
  "EXCHANGE",
  "COMPETITION",
  "VOLUNTEER",
  "COURSE",
];

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

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
  const [actionPlanData, setActionPlanData] = useState(null);
  const [agentData, setAgentData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState("");
  const [error, setError] = useState(null);
  const [planError, setPlanError] = useState(null);

  // Scroll reveal observer
  useEffect(() => {
    if (typeof window === "undefined" || !("IntersectionObserver" in window)) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-revealed");
          }
        });
      },
      { threshold: 0.08, rootMargin: "0px 0px -40px 0px" }
    );

    const revealElements = document.querySelectorAll(".reveal-section");
    revealElements.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, [analysisData, matchData, actionPlanData, agentData]);

  function handleProfileChange(name, value) {
    setProfile((prev) => ({ ...prev, [name]: value }));
  }

  function scrollToWorkspace() {
    const el = document.getElementById("workspace");
    if (el) el.scrollIntoView({ behavior: "smooth" });
  }

  function scrollToHowItWorks() {
    const el = document.getElementById("how-it-works");
    if (el) el.scrollIntoView({ behavior: "smooth" });
  }

  async function handleAnalyze({ opportunity_type, description }) {
    setIsLoading(true);
    setLoadingStage("Analyzing opportunity requirements...");
    setError(null);
    setPlanError(null);

    // Profile validation
    if (profile.gpa && profile.gpa.trim()) {
      const parsedGpa = parseFloat(profile.gpa.replace(",", "."));
      if (isNaN(parsedGpa) || parsedGpa < 0 || parsedGpa > 4.0) {
        setError("Please enter a valid GPA between 0.00 and 4.00.");
        setIsLoading(false);
        setLoadingStage("");
        return;
      }
    }

    if (profile.semester && profile.semester.trim()) {
      const parsedSem = parseInt(profile.semester, 10);
      if (isNaN(parsedSem) || parsedSem < 1 || parsedSem > 14) {
        setError("Please enter a valid semester number (1 to 14).");
        setIsLoading(false);
        setLoadingStage("");
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
      // 1. Primary Flow: Orchestrated Agent Endpoint via api.js
      let agentSuccess = false;
      try {
        setLoadingStage("Executing AI Agent orchestration...");
        const resData = await analyzeWithAgent({
          profile: formattedProfile,
          opportunity_type,
          description,
        });

        setAnalysisData(resData.analysis);
        setMatchData(resData.match);
        setActionPlanData(resData.plan);
        setAgentData(resData.agent);
        agentSuccess = true;
      } catch (agentErr) {
        // Network or endpoint issue: will gracefully fall back to sequential calls below
        console.warn(
          "Agent orchestration unavailable, falling back to deterministic flow:",
          agentErr,
        );
        agentSuccess = false;
      }

      // 2. Safe Fallback: Multi-Request Deterministic Flow
      if (!agentSuccess) {
        setLoadingStage("Analyzing opportunity requirements...");
        const oppResult = await analyzeOpportunity({
          opportunity_type,
          description,
        });
        setAnalysisData(oppResult);

        setLoadingStage("Evaluating profile readiness...");
        const matchResult = await matchProfile({
          profile: formattedProfile,
          opportunity: oppResult,
        });
        setMatchData(matchResult);

        setLoadingStage("Preparing your action plan...");
        try {
          const planResult = await generateActionPlan({
            match_result: matchResult,
            opportunity: oppResult,
            deadline: oppResult?.analysis?.deadline,
          });
          setActionPlanData(planResult);
        } catch (planErr) {
          setPlanError(planErr.message || "Failed to generate action plan.");
        }
        setAgentData({
          actions_executed: [
            "analyze_opportunity",
            "evaluate_profile",
            "build_action_plan",
          ],
          personalization: null,
          ai_personalization_available: false,
        });
      }

      // Smooth scroll to results upon completion
      setTimeout(() => {
        const resultsEl = document.getElementById("results");
        if (resultsEl) {
          resultsEl.scrollIntoView({ behavior: "smooth" });
        }
      }, 150);
    } catch (err) {
      setError(
        err.message ||
          "Failed to process match analysis. Please check if the backend is running at http://localhost:8000.",
      );
    } finally {
      setIsLoading(false);
      setLoadingStage("");
    }
  }

  const hasResults = Boolean(analysisData || matchData);

  return (
    <div className="platform-root">
      <Navbar hasResults={hasResults} />

      <main>
        {/* ========================================================
            1. HERO SECTION (Approved Design Preserved)
            ======================================================== */}
        <section id="hero" className="hero-section">
          <div className="hero-container">
            <div className="hero-content">
              <div className="hero-eyebrow">
                <span className="eyebrow-accent-dot" aria-hidden="true" />
                <span>STUDENT OPPORTUNITY INTELLIGENCE</span>
              </div>

              <h1 className="hero-headline">
                Turn opportunities into{" "}
                <span className="hero-headline-highlight">your next move.</span>
              </h1>

              <p className="hero-description">
                Analyze scholarships, internships, exchanges, and competitions
                against your profile — then turn the gaps into clear next actions.
              </p>

              <div className="hero-cta-group">
                <button
                  type="button"
                  className="primary-hero-btn"
                  onClick={scrollToWorkspace}
                >
                  <span>Analyze Opportunity</span>
                  <span className="btn-arrow-icon" aria-hidden="true">
                    →
                  </span>
                </button>
                <button
                  type="button"
                  className="secondary-hero-btn"
                  onClick={scrollToHowItWorks}
                >
                  See How It Works
                </button>
              </div>

              <div className="hero-supporting-categories">
                <span className="cat-bullet">Scholarship</span>
                <span className="cat-separator" aria-hidden="true">
                  •
                </span>
                <span className="cat-bullet">Internship</span>
                <span className="cat-separator" aria-hidden="true">
                  •
                </span>
                <span className="cat-bullet">Exchange</span>
                <span className="cat-separator" aria-hidden="true">
                  •
                </span>
                <span className="cat-bullet">Competition</span>
              </div>
            </div>

            {/* Right Side: Hero Visual Illustration */}
            <div className="hero-visual-wrapper">
              <img
                src={heroIllustration}
                alt="SkillBridge AI student opportunity and career readiness illustration"
                className="hero-illustration-img"
              />
            </div>
          </div>
        </section>

        {/* ========================================================
            2. OPPORTUNITY MOVING STRIP (Approved Design Preserved)
            ======================================================== */}
        <section
          className="opportunity-marquee-section"
          aria-label="Supported Opportunities"
        >
          <div className="marquee-track">
            <div className="marquee-group">
              {MARQUEE_ITEMS.map((item, idx) => (
                <span key={`a-${idx}`} className="marquee-item">
                  <span>{item}</span>
                  <span className="marquee-separator" aria-hidden="true">
                    •
                  </span>
                </span>
              ))}
            </div>
            <div className="marquee-group" aria-hidden="true">
              {MARQUEE_ITEMS.map((item, idx) => (
                <span key={`b-${idx}`} className="marquee-item">
                  <span>{item}</span>
                  <span className="marquee-separator" aria-hidden="true">
                    •
                  </span>
                </span>
              ))}
            </div>
          </div>
        </section>

        {/* ========================================================
            3. HOW IT WORKS (Approved Design Preserved)
            ======================================================== */}
        <section id="how-it-works" className="workflow-section reveal-section">
          <div className="section-container workflow-container">
            <div className="section-center-header">
              <span className="section-eyebrow">END-TO-END COPILOT</span>
              <h2 className="section-title">From opportunity to action.</h2>
              <p className="section-subtitle">
                A structured four-step journey transforming complex requirements
                into personalized, high-confidence student actions.
              </p>
            </div>

            <div className="timeline-workflow">
              <div className="timeline-track-bar" aria-hidden="true" />

              <div className="timeline-step">
                <div className="timeline-node">
                  <span className="node-number">01</span>
                </div>
                <div className="step-content">
                  <h3 className="step-title">Build Profile</h3>
                  <p className="step-description">
                    Input your study program, semester, GPA, skills, and past
                    activities into your private workspace.
                  </p>
                </div>
              </div>

              <div className="timeline-step">
                <div className="timeline-node">
                  <span className="node-number">02</span>
                </div>
                <div className="step-content">
                  <h3 className="step-title">Analyze Opportunity</h3>
                  <p className="step-description">
                    Paste announcements or brochures; our deterministic parser
                    extracts criteria, deadlines, and benefits instantly.
                  </p>
                </div>
              </div>

              <div className="timeline-step">
                <div className="timeline-node">
                  <span className="node-number">03</span>
                </div>
                <div className="step-content">
                  <h3 className="step-title">Measure Your Match</h3>
                  <p className="step-description">
                    View a transparent, weighted Profile Match Score across
                    eligibility, academic fit, skills, and documents.
                  </p>
                </div>
              </div>

              <div className="timeline-step">
                <div className="timeline-node">
                  <span className="node-number">04</span>
                </div>
                <div className="step-content">
                  <h3 className="step-title">Take Action</h3>
                  <p className="step-description">
                    Pinpoint specific gaps and prepare verified requirements
                    with complete clarity before submitting.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ========================================================
            4. WORKSPACE (Unified Cohesive Surface)
            ======================================================== */}
        <section id="workspace" className="workspace-section reveal-section">
          <div className="section-container">
            <div className="section-header-left">
              <span className="section-eyebrow">YOUR OPPORTUNITY WORKSPACE</span>
              <h2 className="section-title">
                Build your profile.
                <br />
                Analyze your opportunity.
              </h2>
              <p className="section-subtitle">
                Give SkillBridge the context it needs to evaluate your readiness.
              </p>
            </div>

            <div className="workspace-unified-sheet">
              {/* Left Column: Student Profile (WHO AM I?) */}
              <div className="workspace-column column-profile">
                <div className="workspace-col-header">
                  <div className="col-context-tag">
                    <span className="col-step-pill">01</span>
                    <span className="col-context-label">WHO AM I?</span>
                  </div>
                  <h3 className="col-title">STUDENT PROFILE</h3>
                  <p className="col-subtitle">Your academic context</p>
                </div>
                <ProfileForm
                  profile={profile}
                  onChange={handleProfileChange}
                />
              </div>

              {/* Vertical Divider */}
              <div className="workspace-sheet-divider" aria-hidden="true" />

              {/* Right Column: Opportunity Input (WHAT AM I TARGETING?) */}
              <div className="workspace-column column-opportunity">
                <div className="workspace-col-header">
                  <div className="col-context-tag">
                    <span className="col-step-pill">02</span>
                    <span className="col-context-label">WHAT AM I TARGETING?</span>
                  </div>
                  <h3 className="col-title">OPPORTUNITY</h3>
                  <p className="col-subtitle">What are you targeting?</p>
                </div>
                <OpportunityForm
                  onAnalyze={handleAnalyze}
                  isLoading={isLoading}
                  loadingStage={loadingStage}
                  error={error}
                />
              </div>
            </div>
          </div>
        </section>

        {/* ========================================================
            5. YOUR READINESS REPORT (Continuous Story Flow)
            Rendered ONLY when analysis/match results exist.
            Order:
            1. Report Header
            2. Opportunity Snapshot (Core #1)
            3. Profile Match (Core #2)
            4. What's Holding You Back? (Core #2)
            5. AI-Guided Insight (Grounded Personalization Layer)
            6. Action Plan & Roadmap (Core #3)
            ======================================================== */}
        {hasResults && (
          <section id="results" className="results-section reveal-section">
            <div className="section-container">
              {/* Report Header Transition */}
              <div className="section-center-header report-master-header">
                <span className="section-eyebrow">YOUR READINESS REPORT</span>
                <h2 className="section-title">Know where you stand.</h2>
                <p className="section-subtitle">
                  SkillBridge turns the opportunity requirements into a clear
                  view of your current readiness.
                </p>
              </div>

              {/* 1. Opportunity Snapshot */}
              {analysisData && <OpportunityAnalysis data={analysisData} />}

              {/* 2. Profile Match Hero & Breakdown */}
              {matchData && <ProfileMatch data={matchData} />}

              {/* 3. What's Holding You Back? (Gap Analysis) */}
              {matchData && <GapAnalysis data={matchData} />}

              {/* 4. AI-Guided Insight (Grounded Personalization Layer) */}
              {hasResults && (
                <AIInsight
                  personalization={agentData?.personalization}
                  isAvailable={Boolean(agentData?.ai_personalization_available)}
                />
              )}

              {/* 5. Action Plan Roadmap & Verification */}
              {actionPlanData && <ActionPlan data={actionPlanData} />}

              {planError && (
                <div
                  className="alert-banner alert alert-warning"
                  role="alert"
                  style={{ marginTop: "24px" }}
                >
                  <span className="alert-icon" aria-hidden="true">
                    ⚠
                  </span>
                  <span>Action Plan Notice: {planError}</span>
                </div>
              )}
            </div>
          </section>
        )}

        {/* ========================================================
            6. FINAL CTA (Rendered ONLY After Results!)
            ======================================================== */}
        {hasResults && (
          <section className="final-cta-section reveal-section">
            <div className="section-container final-cta-container">
              <h2 className="final-cta-headline">
                Your next opportunity
                <br />
                shouldn&apos;t be guesswork.
              </h2>
              <p className="final-cta-subtext">
                Understand the requirements. Know your gaps. Take the next step.
              </p>
              <button
                type="button"
                className="final-cta-btn"
                onClick={scrollToWorkspace}
              >
                Analyze Another Opportunity
              </button>
            </div>
          </section>
        )}
      </main>

      {/* ========================================================
          7. FOOTER
          ======================================================== */}
      <footer className="platform-footer">
        <div className="footer-container">
          <div className="footer-main-row">
            <div className="footer-brand-col">
              <div className="footer-logo-row">
                <svg
                  viewBox="0 0 32 32"
                  width="28"
                  height="28"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <rect width="32" height="32" rx="6" fill="#1e293b" />
                  <path
                    d="M7 21C11 14 21 14 25 21"
                    stroke="#38bdf8"
                    strokeWidth="2.2"
                    strokeLinecap="round"
                  />
                  <circle cx="16" cy="11" r="2.5" fill="#ffffff" />
                </svg>
                <span className="footer-brand-name">SkillBridge AI</span>
              </div>
              <p className="footer-brand-tagline">
                From Opportunity to Action.
              </p>
              <p className="footer-mission-note">
                Built for university students navigating scholarships, internships,
                student exchanges, and national competitions.
              </p>
            </div>

            <div className="footer-nav-col">
              <h4 className="footer-col-title">Product</h4>
              <ul className="footer-links-list">
                <li>Opportunity Analyzer</li>
                <li>Profile Match</li>
                <li>Gap Analysis</li>
                <li>Action Planner</li>
              </ul>
            </div>

            <div className="footer-nav-col">
              <h4 className="footer-col-title">Hackathon</h4>
              <ul className="footer-links-list">
                <li>SEMESTA 8</li>
                <li>Build with AI</li>
                <li>University Student Copilot</li>
              </ul>
            </div>
          </div>

          <div className="footer-bottom-row">
            <p className="footer-copyright">
              SkillBridge AI — Built for students navigating their next opportunity.
            </p>
            <p className="footer-sub-note">
              Deterministic analyzer &amp; readiness engine.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Dashboard;
