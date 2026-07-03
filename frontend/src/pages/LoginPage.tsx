import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "../api";
import { DisclaimerBanner } from "../components/Layout";

const DEMO_ACCOUNTS = [
  { username: "applicant", password: "applicant123", role: "Submit & resubmit applications" },
  { username: "reviewer", password: "reviewer123", role: "Technical review & decisions" },
  { username: "admin", password: "admin123", role: "Full workflow access" },
  { username: "auditor", password: "auditor123", role: "Read-only audit access" },
];

export function LoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("reviewer");
  const [password, setPassword] = useState("reviewer123");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await authApi.login(username, password);
      navigate("/applications");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  function fillDemo(account: (typeof DEMO_ACCOUNTS)[number]) {
    setUsername(account.username);
    setPassword(account.password);
  }

  return (
    <section className="card">
      <DisclaimerBanner />
      <h2>Sign in — regulatory workflow lab</h2>
      <p className="muted">
        Synthetic demo credentials for role-based access testing. Not connected to any government system.
      </p>
      <form className="form" onSubmit={onSubmit}>
        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="button primary" type="submit" disabled={busy}>
          {busy ? "Signing in…" : "Sign in"}
        </button>
      </form>
      <details className="low-bandwidth">
        <summary>Demo accounts (recruiter walkthrough)</summary>
        <ul className="feature-list">
          {DEMO_ACCOUNTS.map((account) => (
            <li key={account.username}>
              <button type="button" className="link-button" onClick={() => fillDemo(account)}>
                {account.username}
              </button>
              {" / "}
              {account.password} — {account.role}
            </li>
          ))}
        </ul>
      </details>
    </section>
  );
}
