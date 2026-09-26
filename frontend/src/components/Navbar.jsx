function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar-inner">
      <div className="navbar-brand">
        <span className="logo-mark" aria-hidden="true">
          <svg viewBox="0 0 40 40" width="40" height="40" focusable="false">
            <rect width="40" height="40" rx="12" fill="url(#logoBg)" />
            <defs>
              <linearGradient id="logoBg" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#4f46e5" />
                <stop offset="100%" stopColor="#7c3aed" />
              </linearGradient>
            </defs>
            <path
              d="M7 23c7-11 19-11 26 0"
              fill="none"
              stroke="#fff"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
            <path
              d="M11 23v7M29 23v7M7 31h26"
              fill="none"
              stroke="#67e8f9"
              strokeWidth="2.2"
              strokeLinecap="round"
            />
            <path
              d="M20 9l3 4h-6z"
              fill="#fff"
            />
          </svg>
        </span>
        <div className="brand-copy">
          <p className="brand-name">SkillBridge AI</p>
          <p className="brand-tagline">From Opportunity to Action.</p>
        </div>
      </div>

      <p className="copilot-badge">
        <span className="spark" aria-hidden="true">
          ✦
        </span>
        AI Copilot Ready
      </p>
    </header>
  );
}

export default Navbar;
