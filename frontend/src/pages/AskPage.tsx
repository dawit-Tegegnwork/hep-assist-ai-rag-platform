import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { DisclaimerBanner } from "../components/Layout";

const EXAMPLES = {
  en: "What screening tests are approved for hepatitis B in community settings?",
  am: "የሂፓታይቲስ B ምርመራ በcommunity setting እንዴት ይደረጋል?",
};

export function AskPage() {
  const navigate = useNavigate();
  const [question, setQuestion] = useState(EXAMPLES.en);
  const [language, setLanguage] = useState("en");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const created = await api.createQuestion({
        question_text: question,
        language,
        approved_content_only: true,
      });
      const answer = await api.answerQuestion(created.id);
      navigate(`/answers/${answer.id}`, { state: { question: created } });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit question");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <DisclaimerBanner />
      <h2>Health-worker question</h2>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Language
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="en">English</option>
            <option value="am">Amharic (example)</option>
          </select>
        </label>
        <label>
          Question
          <textarea
            rows={5}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            required
          />
        </label>
        <div className="actions">
          <button
            type="button"
            className="button"
            onClick={() => setQuestion(EXAMPLES[language as keyof typeof EXAMPLES])}
          >
            Load example
          </button>
          <button type="submit" className="button primary" disabled={loading}>
            {loading ? "Generating answer…" : "Ask with approved content only"}
          </button>
        </div>
        {error && <p className="error">{error}</p>}
      </form>
    </section>
  );
}
