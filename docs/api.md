# API Reference — HEP Assist AI RAG Platform

Base URL: `http://localhost:8000`  
Prefix: `/api/v1`  
OpenAPI: `/docs`

All endpoints use synthetic data. Outputs are not medical advice.

## Health

### `GET /health`

```json
{"status": "ok", "service": "HEP Assist AI RAG Platform"}
```

## Q&A

### `POST /api/v1/questions`

Create a health-worker question.

**Body:**
```json
{
  "question_text": "What hepatitis B screening tests are approved?",
  "language": "en",
  "worker_id": "synthetic-worker-001",
  "approved_content_only": true
}
```

### `POST /api/v1/questions/{question_id}/answer`

Run RAG retrieval, safety checks, and LLM generation. Creates audit event `qa.answer`.

**Response highlights:**
- `answer_text`, `citations[]`, `risk_flags[]`, `hallucination_flags[]`
- `refused`, `refusal_reason`, `review_status`
- `disclaimer`

### `GET /api/v1/questions`

List all questions with latest answer.

### `GET /api/v1/questions/{question_id}`

Question detail with latest answer.

### `POST /api/v1/answers/{answer_id}/review`

**Body:**
```json
{"action": "approve", "reviewer_comment": "Looks grounded"}
```

Actions: `approve`, `reject`, `request_changes`

### `GET /api/v1/dashboard/qa-summary`

Counts: pending, approved, rejected, changes_requested, total_questions, total_answers, refused_answers

## Evaluation

### `POST /api/v1/evaluation/run`

Runs golden synthetic test questions. Returns citation rate, refusal rate, avg retrieval score, per-question results. Creates audit event `evaluation.run`.

## Audit

### `GET /api/v1/audit?limit=50&action=qa.answer`

List audit events. Filter by `action` optionally.

## Legacy endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/notes` | Create synthetic clinical note |
| POST | `/api/v1/notes/{id}/extract` | Run structured extraction |
| POST | `/api/v1/extractions/{id}/review` | Review extraction |
| GET | `/api/v1/dashboard/summary` | Legacy note dashboard |
| POST | `/api/v1/clinical/preprocess` | Text preprocessing |
| POST | `/api/v1/guidelines/search` | Keyword guideline search |
| POST | `/api/v1/soap-note` | SOAP draft |

## Refusal reason codes

| Code | Meaning |
|------|---------|
| `emergency_or_urgent_care` | Emergency language detected |
| `diagnosis_request_not_supported` | Diagnosis request |
| `prescribing_request_not_supported` | Prescribing/dosing request |
| `no_approved_content_match` | No retrieval matches |
| `low_retrieval_confidence` | Top score below threshold |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MEDIMIND_DATABASE_URL` | SQLite file | PostgreSQL in Docker |
| `MEDIMIND_EMBEDDING_PROVIDER` | `fastembed` (mock in Docker/tests) | `mock` or `fastembed` |
| `MEDIMIND_RETRIEVAL_MIN_SCORE` | `0.35` | Refusal threshold |
| `OPENAI_API_KEY` | unset | Enables OpenAI-compatible LLM |
