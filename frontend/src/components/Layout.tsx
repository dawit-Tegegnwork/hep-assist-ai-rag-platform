import { Link, NavLink, Outlet } from "react-router-dom";

export function Layout() {
  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>HEP Assist AI RAG Platform</h1>
          <p className="tagline">Synthetic demo only — not medical advice</p>
        </div>
        <nav>
          <NavLink to="/ask">Ask</NavLink>
          <NavLink to="/review">Review</NavLink>
          <NavLink to="/evaluation">Evaluation</NavLink>
          <NavLink to="/audit">Audit</NavLink>
        </nav>
      </header>
      <main className="main">
        <Outlet />
      </main>
      <footer className="footer">
        Portfolio reference implementation with synthetic data. Human review required before any clinical use.
      </footer>
    </div>
  );
}

export function DisclaimerBanner() {
  return (
    <div className="banner warning" role="alert">
      Synthetic data only. This assistant does not provide medical advice and is not deployed in production.
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

export function HomeLink() {
  return <Link to="/">← Home</Link>;
}
