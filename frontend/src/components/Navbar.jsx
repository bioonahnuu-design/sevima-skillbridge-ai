import { useState } from "react";

function Navbar({ hasResults = false }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  function scrollToSection(id) {
    setMobileMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  }

  return (
    <header className="navbar">
      <div className="navbar-container">
        <a
          href="#hero"
          className="navbar-brand"
          onClick={(e) => {
            e.preventDefault();
            scrollToSection("hero");
          }}
        >
          <span className="brand-logo" aria-hidden="true">
            <svg
              viewBox="0 0 36 36"
              width="36"
              height="36"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <rect width="36" height="36" rx="8" fill="#0b192c" />
              <path
                d="M8 24C12 16 24 16 28 24"
                stroke="#38bdf8"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
              <path
                d="M12 24V28M24 24V28M8 28H28"
                stroke="#94a3b8"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
              <circle cx="18" cy="12" r="3" fill="#ffffff" />
            </svg>
          </span>
          <div className="brand-text">
            <span className="brand-name">SkillBridge AI</span>
            <span className="brand-tagline">From Opportunity to Action.</span>
          </div>
        </a>

        {/* Desktop Navigation */}
        <nav className="navbar-nav" aria-label="Main Navigation">
          <button
            type="button"
            className="nav-link"
            onClick={() => scrollToSection("hero")}
          >
            Home
          </button>
          <button
            type="button"
            className="nav-link"
            onClick={() => scrollToSection("how-it-works")}
          >
            How It Works
          </button>
          <button
            type="button"
            className="nav-link"
            onClick={() => scrollToSection("workspace")}
          >
            Analyzer
          </button>
          {hasResults && (
            <button
              type="button"
              className="nav-link nav-link-active"
              onClick={() => scrollToSection("results")}
            >
              Results
            </button>
          )}
        </nav>

        {/* Right CTA */}
        <div className="navbar-cta-wrap">
          <button
            type="button"
            className="nav-cta-btn"
            onClick={() => scrollToSection("workspace")}
          >
            <span>Analyze Opportunity</span>
            <span className="btn-arrow" aria-hidden="true">→</span>
          </button>

          {/* Mobile Menu Toggle Button */}
          <button
            type="button"
            className="mobile-menu-toggle"
            aria-label="Toggle navigation menu"
            aria-expanded={mobileMenuOpen}
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <span className="hamburger-line" />
            <span className="hamburger-line" />
            <span className="hamburger-line" />
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="mobile-menu-drawer" role="dialog" aria-label="Mobile Navigation">
          <button
            type="button"
            className="mobile-nav-link"
            onClick={() => scrollToSection("hero")}
          >
            Home
          </button>
          <button
            type="button"
            className="mobile-nav-link"
            onClick={() => scrollToSection("how-it-works")}
          >
            How It Works
          </button>
          <button
            type="button"
            className="mobile-nav-link"
            onClick={() => scrollToSection("workspace")}
          >
            Analyzer
          </button>
          {hasResults && (
            <button
              type="button"
              className="mobile-nav-link"
              onClick={() => scrollToSection("results")}
            >
              Results
            </button>
          )}
          <button
            type="button"
            className="mobile-cta-btn"
            onClick={() => scrollToSection("workspace")}
          >
            Analyze Opportunity →
          </button>
        </div>
      )}
    </header>
  );
}

export default Navbar;
