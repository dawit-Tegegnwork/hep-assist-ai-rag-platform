import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { DisclaimerBanner } from "../components/Layout";

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api/v1";

const HEP_FEATURES = [
  "AI layered on approved synthetic health guidance — not open-ended chat",
  "Approved-content-only answers with citations and retrieval scores",
  "Human-in-the-loop review before trusting any AI output",
  "Safety refusal for emergency, diagnosis, and prescribing requests",
  "Risk and hallucination flags on the mock LLM path",
  "Amharic example questions (architecture demo, not certified translation)",
  "Audit trail for questions, answers, reviews, and evaluation runs",
  "Golden evaluation set with pass/fail scoring",
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
      <h2>HEP Assist AI — health-worker guidance with safe AI layer</h2>
      <p>
        Portfolio reference implementation for Last Mile Health / Senior AI Engineer-style roles.
        Community health workers already follow approved protocols; this demo shows AI retrieval and
        generation on top of that content only. <strong>Synthetic data only</strong>;{" "}
        <strong>mock LLM by default</strong>; not medical advice or production clinical software.
      </p>
      <ul className="feature-list">
        {HEP_FEATURES.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      <div className="actions">
        <Link className="button primary" to="/ask">Ask a health-worker question</Link>
        <Link className="button" to="/review">Review queue</Link>
        <Link className="button" to="/evaluation">Run evaluation</Link>
        <Link className="button" to="/audit">Audit log</Link>
      </div>
      <details className="low-bandwidth">
        <summary>10-minute interview demo script</summary>
        <ol className="feature-list">
          <li>Ask a safe hepatitis B screening question (English)</li>
          <li>Show answer citations and pending human review</li>
          <li>Ask an unsafe prescribing question — show refusal</li>
          <li>Try Amharic example — note local-language demo flags</li>
          <li>Approve an answer in the review queue</li>
          <li>Open audit log — qa.answer and qa.answer.review events</li>
          <li>Run evaluation — pass/fail on golden synthetic set</li>
        </ol>
        <p>
          Full script: <code>docs/interview-demo-script.md</code> · API automation:{" "}
          <code>./scripts/demo_workflow.sh</code>
        </p>
      </details>
      <details className="low-bandwidth">
        <summary>Low-bandwidth / offline design notes</summary>
        <p>
          Lightweight UI, minimal assets, paginated API. For true offline use, cache approved content
          chunks locally and queue questions for sync. See <code>docs/offline-first-design.md</code>.
        </p>
      </details>
      <details className="low-bandwidth">
        <summary>Healthcare interoperability lab (same repo)</summary>
        <p>
          Synthetic integration lab inspired by OpenMRS, OpenELIS, DHIS2, and FHIR — validates,
          transforms, audits, and exports payloads. Not connected to real hospital systems. See{" "}
          <code>interop-lab/README.md</code>.
        </p>
        <div className="actions">
          <a className="button" href="/interop/dashboard" target="_blank" rel="noreferrer">
            Interop dashboard
          </a>
          <a
            className="button"
            href={`${API_BASE.replace("/api/v1", "")}/docs#/interop`}
            target="_blank"
            rel="noreferrer"
          >
            Interop API docs
          </a>
        </div>
        <p>
          Demo: <code>./scripts/interop_demo.sh http://127.0.0.1:8000</code>
        </p>
      </details>
      <details className="low-bandwidth">
        <summary>Regulatory modernization lab (same repo)</summary>
        <p>
          This repository also includes a synthetic eRIS-style regulatory application workflow
          (applications, role-based sign-in, transition audit). It is a separate portfolio module —
          see <code>/applications</code> and <code>/login</code>.
        </p>
        <div className="actions">
          <Link className="button" to="/applications">Applications queue</Link>
          <Link className="button" to="/login">Sign in (regulatory demo)</Link>
        </div>
      </details>
    </section>
  );
}
