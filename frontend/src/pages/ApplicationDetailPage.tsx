import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  AuditTrailEvent,
  RegulatoryApplication,
  getStoredUser,
  isAuthenticated,
  regulatoryApi,
} from "../api";
import { DisclaimerBanner, HomeLink } from "../components/Layout";

const REVIEWER_ACTIONS: Record<string, { action: string; label: string }[]> = {
  submitted: [{ action: "start_technical_review", label: "Start technical review" }],
  technical_review: [
    { action: "request_clarification", label: "Request clarification" },
    { action: "approve", label: "Approve" },
    { action: "reject", label: "Reject" },
  ],
  resubmitted: [{ action: "start_technical_review", label: "Resume technical review" }],
};

export function ApplicationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const user = getStoredUser();
  const [app, setApp] = useState<RegulatoryApplication | null>(null);
  const [audit, setAudit] = useState<AuditTrailEvent[]>([]);
  const [comment, setComment] = useState("");
  const [resubmitDossier, setResubmitDossier] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }
    if (id) load(id);
  }, [id, navigate]);

  async function load(appId: string) {
    try {
      const [application, trail] = await Promise.all([
        regulatoryApi.getApplication(appId),
        regulatoryApi.auditTrail(appId),
      ]);
      setApp(application);
      setResubmitDossier(application.dossier_summary);
      setAudit(trail);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load application");
    }
  }

  async function runTransition(action: string) {
    if (!id) return;
    setBusy(true);
    setError(null);
    try {
      await regulatoryApi.transition(id, action, comment || undefined);
      setComment("");
      await load(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Transition failed");
    } finally {
      setBusy(false);
    }
  }

  async function onResubmit(event: FormEvent) {
    event.preventDefault();
    if (!id) return;
    setBusy(true);
    try {
      await regulatoryApi.resubmit(id, {
        dossier_summary: resubmitDossier,
        supporting_documents: ["module_2.3.pdf", "clarification_response.pdf"],
        applicant_note: comment || "Addressed clarification request",
      });
      setComment("");
      await load(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Resubmit failed");
    } finally {
      setBusy(false);
    }
  }

  if (!app) {
    return (
      <section className="card">
        <HomeLink />
        <p>Loading application…</p>
      </section>
    );
  }

  const reviewerActions =
    user?.role === "technical_reviewer" || user?.role === "admin"
      ? REVIEWER_ACTIONS[app.status] ?? []
      : [];

  return (
    <section className="card">
      <DisclaimerBanner />
      <p><Link to="/applications">← Applications</Link></p>
      <h2>{app.reference_number}</h2>
      <p><strong>{app.product_name}</strong> — {app.application_type.replace(/_/g, " ")}</p>
      <p className="muted">{app.applicant_organization}</p>
      <p>
        Status: <span className={`status-pill status-${app.status}`}>{app.status.replace(/_/g, " ")}</span>
      </p>
      {app.assigned_reviewer && <p className="muted">Reviewer: {app.assigned_reviewer}</p>}
      {app.last_comment && <p className="banner caution">Last comment: {app.last_comment}</p>}

      <h3>Dossier summary</h3>
      <p>{app.dossier_summary}</p>
      {app.supporting_documents.length > 0 && (
        <>
          <h3>Supporting documents</h3>
          <ul>
            {app.supporting_documents.map((doc) => (
              <li key={doc}>{doc}</li>
            ))}
          </ul>
        </>
      )}

      {error && <p className="error">{error}</p>}

      {reviewerActions.length > 0 && (
        <div className="actions">
          <label>
            Review comment
            <input value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Optional comment" />
          </label>
          {reviewerActions.map((item) => (
            <button
              key={item.action}
              type="button"
              className="button"
              disabled={busy}
              onClick={() => runTransition(item.action)}
            >
              {item.label}
            </button>
          ))}
        </div>
      )}

      {app.status === "clarification_requested" &&
        (user?.role === "applicant" || user?.role === "admin") && (
          <form className="form" onSubmit={onResubmit}>
            <h3>Resubmit with updates</h3>
            <label>
              Updated dossier summary
              <textarea
                value={resubmitDossier}
                onChange={(e) => setResubmitDossier(e.target.value)}
                rows={4}
                required
              />
            </label>
            <label>
              Note to reviewer
              <input value={comment} onChange={(e) => setComment(e.target.value)} />
            </label>
            <button className="button primary" type="submit" disabled={busy}>
              Resubmit application
            </button>
          </form>
        )}

      <h3>Audit trail</h3>
      {audit.length === 0 ? (
        <p className="muted">No audit events recorded yet.</p>
      ) : (
        <table className="audit-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Action</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {audit.map((event) => (
              <tr key={event.id}>
                <td>{new Date(event.created_at).toLocaleString()}</td>
                <td>{event.action}</td>
                <td>
                  <code>{JSON.stringify(event.metadata)}</code>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
