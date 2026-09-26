import Navbar from "../components/Navbar.jsx";
import ProfileForm from "../components/ProfileForm.jsx";
import OpportunityForm from "../components/OpportunityForm.jsx";

function Dashboard() {
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
            Analyze scholarships, internships, exchanges and other
            opportunities against your profile — then discover your gaps and
            the actions that matter most.
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
            <ProfileForm />
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
            <OpportunityForm />
          </article>
        </section>
      </main>
    </div>
  );
}

export default Dashboard;
