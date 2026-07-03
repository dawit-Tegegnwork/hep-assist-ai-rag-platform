import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  RegulatoryApplication,
  RegulatorySummary,
  authApi,
  getStoredUser,
  isAuthenticated,
  regulatoryApi,
} from "../api";
import { DisclaimerBanner } from "../components/Layout";

const STATUS_LABELS: Record<string, string> = {
  submitted: "Submitted",
  technical_review: "Technical review",
  clarification_requested: "Clarification requested",
  resubmitted: "Resubmitted",
  approved: "Approved",
  rejected: "Rejected",
};

export function ApplicationsPage() {
  const navigate = useNavigate();
  const user = getStoredUser();
  const [items, setItems] = useState<RegulatoryApplication[]>([]);
  const [summary, setSummary] = useState<RegulatorySummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [productName, setProductName] = useState("Synthetic Product Demo");
  const [dossier, setDossier] = useState(
    "Synthetic marketing authorization dossier for portfolio demonstration with sufficient detail for review.",
  );

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }
    load();
  }, [navigate]);

  async function load() {
    try {
      const apps = await regulatoryApi.listApplications();
      setItems(apps);
      if (user?.role === "technical_reviewer" || user?.role === "admin" || user?.role === "auditor") {
        setSummary(await regulatoryApi.summary());
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load applications");
    }
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      const app = await regulatoryApi.submitApplication({
        product_name: productName,
        application_type: "marketing_authorization",
        applicant_organization: user?.organization ?? "Synthetic Pharma Ltd",
        dossier_summary: dossier,
        supporting_documents: ["module_2.3.pdf"],
      });
      setShowForm(false);
      navigate(`/applications/${app.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Submit failed");
    }
  }

  function logout() {
    authApi.logout();
    navigate("/login");
  }

  return (
    <section className="card">
      <DisclaimerBanner />
      <div className="row-between">
        <div>
          <h2>Regulatory applications</h2>
          {user && (
            <p className="muted">
              Signed in as {user.display_name} ({user.role}) — {user.organization}
            </p>
          )}
        </div>
        <button type="button" className="button" onClick={logout}>
          Sign out
        </button>
      </div>

      {summary && (
        <div className="stats">
          <span>Submitted: {summary.submitted}</span>
          <span>In review: {summary.technical_review}</span>
          <span>Clarification: {summary.clarification_requested}</span>
          <span>Resubmitted: {summary.resubmitted}</span>
          <span>Approved: {summary.approved}</span>
          <span>Rejected: {summary.rejected}</span>
        </div>
      )}

      {error && <p className="error">{error}</p>}

      {(user?.role === "applicant" || user?.role === "admin") && (
        <div className="actions">
          <button type="button" className="button primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? "Cancel" : "New application"}
          </button>
        </div>
      )}

      {showForm && (
        <form className="form" onSubmit={onSubmit}>
          <label>
            Product name
            <input value={productName} onChange={(e) => setProductName(e.target.value)} required />
          </label>
          <label>
            Dossier summary
            <textarea value={dossier} onChange={(e) => setDossier(e.target.value)} rows={4} required />
          </label>
          <button className="button primary" type="submit">
            Submit application
          </button>
        </form>
      )}

      <ul className="review-list">
        {items.map((app) => (
          <li key={app.id}>
            <Link to={`/applications/${app.id}`}>
              <strong>{app.reference_number}</strong> — {app.product_name}
            </Link>
            <span className={`status-pill status-${app.status}`}>
              {STATUS_LABELS[app.status] ?? app.status}
            </span>
            <p className="muted">{app.applicant_organization}</p>
          </li>
        ))}
      </ul>
      {items.length === 0 && <p className="muted">No applications yet.</p>}
    </section>
  );
}
