import { useState } from "react";
import { api, EvaluationResult } from "../api";
import { HepDisclaimerBanner } from "../components/Layout";

export function EvaluationPage() {
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.runEvaluation();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Evaluation failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <HepDisclaimerBanner />
      <h2>Evaluation dashboard</h2>
      <p>Runs golden synthetic test questions through retrieval, safety gates, and pass/fail scoring.</p>
      <button className="button primary" onClick={run} disabled={loading}>
        {loading ? "Running evaluation…" : "Run evaluation"}
      </button>
      {error && <p className="error">{error}</p>}
      {result && (
        <>
          <div className="stats">
            <span>Total: {result.total_questions}</span>
            <span>Passed: {result.passed}</span>
            <span>Pass rate: {(result.pass_rate * 100).toFixed(0)}%</span>
            <span>Answered: {result.answered}</span>
            <span>Refused: {result.refused}</span>
            <span>Citation rate: {(result.citation_rate * 100).toFixed(0)}%</span>
            <span>Avg retrieval: {result.avg_retrieval_score}</span>
          </div>
          <p className="muted">{result.disclaimer}</p>
          <table className="table">
            <thead>
              <tr>
                <th>Question</th>
                <th>Lang</th>
                <th>Answered</th>
                <th>Refused</th>
                <th>Citations</th>
                <th>Top score</th>
                <th>Pass</th>
              </tr>
            </thead>
            <tbody>
              {result.results.map((row) => (
                <tr key={row.question} className={row.passed ? "pass" : "fail"}>
                  <td>{row.question.slice(0, 80)}{row.question.length > 80 ? "…" : ""}</td>
                  <td>{row.language}</td>
                  <td>{row.answered ? "yes" : "no"}</td>
                  <td>{row.refused ? "yes" : "no"}</td>
                  <td>{row.has_citations ? "yes" : "no"}</td>
                  <td>{row.top_score}</td>
                  <td>{row.passed ? "pass" : "fail"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </section>
  );
}
