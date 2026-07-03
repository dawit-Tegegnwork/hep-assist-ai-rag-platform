import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, Answer, Question } from "../api";
import { HepDisclaimerBanner, RiskBanner } from "../components/Layout";

export function AnswerPage() {
  const { id } = useParams<{ id: string }>();
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [question, setQuestion] = useState<Question | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    async function load() {
      try {
        const questions = await api.listQuestions();
        for (const item of questions) {
          if (item.latest_answer?.id === id) {
            setQuestion(item.question);
            setAnswer(item.latest_answer);
            return;
          }
        }
        setError("Answer not found");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load answer");
      }
    }
    load();
  }, [id]);

  if (error) return <p className="error">{error}</p>;
  if (!answer) return <p>Loading answer…</p>;

  return (
    <section className="card">
      <HepDisclaimerBanner />
      <h2>Answer with citations</h2>
      {question && (
        <div className="meta">
          <strong>Question:</strong> {question.question_text}
          <span className="pill">{question.language}</span>
        </div>
      )}
      <RiskBanner
        flags={[...answer.risk_flags, ...answer.hallucination_flags]}
        refused={answer.refused}
        refusalReason={answer.refusal_reason}
      />
      <article className="answer-text">{answer.answer_text}</article>
      <p className="muted">{answer.disclaimer}</p>
      <h3>Citations ({answer.citations.length})</h3>
      {answer.citations.length === 0 ? (
        <p className="muted">No citations — answer refused or no approved match.</p>
      ) : (
        <ul className="citation-list">
          {answer.citations.map((c) => (
            <li key={c.chunk_id}>
              <strong>{c.title}</strong> — score {c.score}
              <p className="muted">{c.source}</p>
              <p>{c.excerpt}</p>
            </li>
          ))}
        </ul>
      )}
      <div className="actions">
        <Link className="button" to="/review">Go to review</Link>
        <Link className="button primary" to="/ask">Ask another</Link>
      </div>
    </section>
  );
}
