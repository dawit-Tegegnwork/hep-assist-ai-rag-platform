import { Link, NavLink, Outlet } from "react-router-dom";
import { authApi, getStoredUser, isAuthenticated } from "../api";

export function Layout() {
  const user = getStoredUser();
  const signedIn = isAuthenticated();

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>eRIS Modernization Lab</h1>
          <p className="tagline">Synthetic regulatory workflow demo — not connected to EFDA or any government system</p>
        </div>
        <nav>
          <NavLink to="/">Home</NavLink>
          <NavLink to="/ask">Health Q&A</NavLink>
          <NavLink to="/review">Q&A review</NavLink>
          <NavLink to="/evaluation">Evaluation</NavLink>
          <NavLink to="/applications">Applications</NavLink>
          <NavLink to="/audit">Audit log</NavLink>
          {signedIn ? (
            <button type="button" className="link-button" onClick={() => { authApi.logout(); window.location.href = "/login"; }}>
              Sign out ({user?.role})
            </button>
          ) : (
            <NavLink to="/login">Sign in</NavLink>
          )}
        </nav>
      </header>
      <main className="main">
        <Outlet />
      </main>
      <footer className="footer">
        Portfolio modernization lab with synthetic data. Demonstrates stabilization, migration readiness, and release discipline patterns.
      </footer>
    </div>
  );
}

export function DisclaimerBanner() {
  return (
    <div className="banner warning" role="alert">
      Synthetic portfolio reference only. Not real eRIS. Not connected to EFDA or any government regulatory system.
    </div>
  );
}

export function RiskBanner({ flags, refused, refusalReason }: {
  flags: string[];
  refused?: boolean;
  refusalReason?: string | null;
}) {
  if (!refused && flags.length === 0) return null;
  return (
    <div className={`banner ${refused ? "danger" : "caution"}`}>
      {refused && <strong>Refused: </strong>}
      {refused && refusalReason ? <span>{refusalReason.replace(/_/g, " ")}. </span> : null}
      {flags.length > 0 && <span>Flags: {flags.join(", ")}</span>}
    </div>
  );
}

export function HepDisclaimerBanner() {
  return (
    <div className="banner warning" role="alert">
      Synthetic portfolio reference only. Mock LLM by default. Approved-content demo — not medical advice,
      not production, not certified translation.
    </div>
  );
}

export function HomeLink() {
  return <Link to="/">← Home</Link>;
}
