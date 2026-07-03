# Screenshots

Captured from the live demo UI (synthetic data only).

| File | Page | URL |
|------|------|-----|
| `home.png` | HEP Assist home + interview script | http://localhost:5173/ |
| `ask.png` | Ask question form | http://localhost:5173/ask |
| `answer.png` | Answer with citations | After submitting a question |
| `review.png` | Human review dashboard | http://localhost:5173/review |
| `evaluation.png` | Evaluation pass/fail dashboard | http://localhost:5173/evaluation |
| `audit.png` | Audit event log | http://localhost:5173/audit |
| `swagger.png` | OpenAPI docs | http://localhost:8000/docs |

## Recapture

```bash
docker compose up --build
# Headless Chrome:
google-chrome --headless --screenshot=docs/screenshots/ask.png http://127.0.0.1:5173/ask
# Or with Playwright:
python scripts/capture_screenshots.py
```
