import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { DisclaimerBanner } from "../components/Layout";

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api/v1";

const FEATURES = [
  "Vector RAG over approved synthetic health content",
  "Human-in-the-loop review for every AI answer",
  "Safety gates for emergency, diagnosis, and prescribing requests",
  "Citation display with retrieval scores",
  "Amharic example questions (architecture demo)",
  "Audit log for every AI interaction",
  "Evaluation dashboard with golden test questions",
];

export function HomePage() {
  const [apiStatus, setApiStatus] = useState<"checking" | "ok" | "down">("checking");

  useEffect(() => {
    fetch("/health/live")
      .then((r) => (r.ok ? setApiStatus("ok") : setApiStatus("down")))
      .catch(() => setApiStatus("down"));
  }, []);

  return (
    <section className="card">
      <DisclaimerBanner />
      <p className={`api-status ${apiStatus}`}>
        API status: {apiStatus === "checking" ? "checking…" : apiStatus === "ok" ? "connected" : "unavailable"}
        {apiStatus === "ok" && (
          <> — <a href={`${API_BASE.replace("/api/v1", "")}/docs`} target="_blank" rel="noreferrer">OpenAPI docs</a></>
        )}
      </p>
      <h2>Health-worker AI assistant (portfolio demo)</h2>
      <p>
        Production-style reference implementation inspired by Last Mile Health / HEP Assist AI
        requirements. Uses synthetic data only and runs without paid API keys by default.
      </p>
      <ul className="feature-list">
        {FEATURES.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      <div className="actions">
        <Link className="button primary" to="/ask">Ask a question</Link>
        <Link className="button" to="/review">Review dashboard</Link>
        <Link className="button" to="/evaluation">Run evaluation</Link>
      </div>
      <details className="low-bandwidth">
        <summary>Low-bandwidth / offline design notes</summary>
        <p>
          This UI uses system fonts, minimal assets, and paginated API calls. For true offline
          use, cache approved content chunks locally and queue questions for sync when connectivity
          returns. Voice/IVR could be added via STT → language detect → RAG Q&A → TTS.
        </p>
      </details>
    </section>
  );
}
