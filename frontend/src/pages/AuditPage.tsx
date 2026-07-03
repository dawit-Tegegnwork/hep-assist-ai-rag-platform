import { useEffect, useState } from "react";
import { api, AuditEvent } from "../api";
import { DisclaimerBanner } from "../components/Layout";

export function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listAudit(100)
      .then(setEvents)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load audit log"));
  }, []);

  return (
    <section className="card">
      <DisclaimerBanner />
      <h2>Audit log</h2>
      <p className="muted">Every AI answer and review action is recorded for demo accountability.</p>
      {error && <p className="error">{error}</p>}
      <table className="table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Action</th>
            <th>Entity</th>
            <th>Metadata</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr key={event.id}>
              <td>{new Date(event.created_at).toLocaleString()}</td>
              <td>{event.action}</td>
              <td>{event.entity_type} {event.entity_id?.slice(0, 8)}</td>
              <td><code>{JSON.stringify(event.metadata).slice(0, 120)}</code></td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
