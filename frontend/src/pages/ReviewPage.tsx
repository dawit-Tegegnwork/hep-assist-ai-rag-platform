import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, QuestionDetail, QASummary } from "../api";
import { DisclaimerBanner } from "../components/Layout";

export function ReviewPage() {
  const [items, setItems] = useState<QuestionDetail[]>([]);
  const [summary, setSummary] = useState<QASummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  async function load() {
    try {
      const [questions, stats] = await Promise.all([api.listQuestions(), api.qaSummary()]);
      setItems(questions);
      setSummary(stats);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load review queue");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function review(answerId: string, action: string) {
    setBusyId(answerId);
    try {
      await api.reviewAnswer(answerId, action, `Demo ${action} from review dashboard`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Review failed");
    } finally {
      setBusyId(null);
    }
  }

  const pending = items.filter((i) => i.latest_answer?.review_status === "pending");

  return (
    <section className="card">
      <DisclaimerBanner />
      <h2>Human review dashboard</h2>
      {summary && (
        <div className="stats">
          <span>Pending: {summary.pending_review}</span>
          <span>Approved: {summary.approved}</span>
          <span>Rejected: {summary.rejected}</span>
          <span>Refused answers: {summary.refused_answers}</span>
        </div>
      )}
      {error && <p className="error">{error}</p>}
      {pending.length === 0 ? (
        <p className="muted">No pending answers. <Link to="/ask">Ask a question</Link></p>
      ) : (
        <ul className="review-list">
          {pending.map((item) => (
            <li key={item.question.id}>
              <p><strong>Q:</strong> {item.question.question_text}</p>
              <p className="muted">{item.latest_answer?.answer_text.slice(0, 200)}…</p>
              <div className="actions">
                <button
                  className="button primary"
                  disabled={busyId === item.latest_answer?.id}
                  onClick={() => review(item.latest_answer!.id, "approve")}
                >
                  Approve
                </button>
                <button
                  className="button"
                  disabled={busyId === item.latest_answer?.id}
                  onClick={() => review(item.latest_answer!.id, "reject")}
                >
                  Reject
                </button>
                <button
                  className="button"
                  disabled={busyId === item.latest_answer?.id}
                  onClick={() => review(item.latest_answer!.id, "request_changes")}
                >
                  Request changes
                </button>
                {item.latest_answer && (
                  <Link className="button" to={`/answers/${item.latest_answer.id}`}>View</Link>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
