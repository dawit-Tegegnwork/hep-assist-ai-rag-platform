# Interview Demo Script — HEP Assist AI RAG Platform

**~10 minutes** · portfolio reference implementation · synthetic data only · mock LLM by default

Use this script to show AI modernization **on top of** existing health-worker guidance — not a generic chatbot.

## Setup (before the interview)

```bash
docker compose up --build
# Optional automated API walkthrough:
./scripts/demo_workflow.sh http://127.0.0.1:8000
```

Open:

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

## Talking opener (30 sec)

> "This is a portfolio reference implementation inspired by HEP Assist / Last Mile Health. Health workers already use approved protocols; we layer retrieval and generation on that content only, with human review and audit. It's synthetic data, mock LLM by default, not production clinical software."

---

## 1. Ask a safe question (2 min)

**UI:** Home → **Ask a question**

**Say:** "Workers ask in the field; we only answer from approved synthetic chunks."

**Do:**

1. Language: **English**
2. Question: `What hepatitis B screening tests are approved for community health workers?`
3. Click **Ask with approved content only**

**Point out:** `approved_content_only: true` in API — retrieval must match ministry-style content.

---

## 2. Show citations and safety framing (2 min)

**UI:** Answer page (auto-navigated)

**Say:** "Every non-refused answer includes citations with retrieval scores — workers can verify against source excerpts."

**Show:**

- Citation list (title, score, excerpt)
- Disclaimer: synthetic demo, not medical advice
- `review_status: pending` — nothing is trusted until a human approves

---

## 3. Ask an unsafe question (1 min)

**UI:** Ask → new question

**Say:** "Emergency, diagnosis, and prescribing requests are refused before we waste retrieval or generate harmful text."

**Do:**

- Question: `Prescribe antiviral dose for hepatitis C patient`
- Submit

**Show:**

- `refused: true`
- `refusal_reason: prescribing_request_not_supported`
- No citations
- Risk banner in UI

**Optional API:**

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{"question_text":"Prescribe antiviral dose for hepatitis C patient","language":"en"}' | jq .
```

---

## 4. Amharic example — honest limits (1 min)

**UI:** Ask → Language **Amharic (example)**

**Do:** Load example or use:

```
የሂፓታይቲስ B ምርመራ በcommunity setting እንዴት ይደረጋል?
```

**Say:** "We index Amharic example chunks to discuss local-language architecture. Flags `local_language_demo` and `not_certified_translation` make clear this is not certified ministry content."

**Unsafe Amharic example (refusal):**

```
ለሂፓታይቲስ C ታዳሲ antiviral መድሃኒት መጠን ይመድቡልኝ
```

---

## 5. Human review queue (1 min)

**UI:** **Review dashboard**

**Say:** "Human-in-the-loop — reviewers approve, reject, or request changes before field use."

**Do:** Approve the safe screening answer with comment `Interview demo approval`

**Show:** Status changes to `approved`; audit will record `qa.answer.review`

---

## 6. Audit log (1 min)

**UI:** **Audit** (nav) or `GET /api/v1/audit`

**Say:** "Every question, answer, review, and evaluation run is logged for accountability."

**Point out actions:**

- `qa.question.create`
- `qa.answer` (with `citation_count`, `refused`, `risk_flags`)
- `qa.answer.review`
- `evaluation.run`

---

## 7. Run evaluation (2 min)

**UI:** **Evaluation** → **Run evaluation**

**Say:** "We maintain a golden synthetic set with pass/fail scoring — citation rate, refusal on unsafe cases, retrieval quality."

**Show:**

- Aggregate: citation rate, refusal rate, **pass rate**
- Per-row pass/fail in table
- Disclaimer: not clinical validation

---

## 8. Close with architecture (optional)

**Points:**

- Mock LLM default — no API keys for interview
- Offline-first: cache approved chunks, queue sync ([offline-first-design.md](offline-first-design.md))
- Production gaps: auth, certified translation, Alembic, compliance

## Automated alternative

```bash
./scripts/demo_workflow.sh http://127.0.0.1:8000
```

Covers steps 1–7 via curl + JSON output.

## Screenshots

Capture after stack is up:

```bash
python scripts/capture_screenshots.py
```

Outputs under `docs/screenshots/`.
