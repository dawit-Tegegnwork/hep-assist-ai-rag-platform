# Production deployment guide

This project is a **portfolio reference implementation** with production-style engineering. It is not a certified medical device and must not be used with real patient data without a full compliance review.

## Production checklist

| Item | Status in this repo |
|------|---------------------|
| Health probes (`/health/live`, `/health/ready`) | Implemented |
| Structured request logging + request IDs | Implemented |
| Rate limiting | Implemented (configurable) |
| CORS configuration | Environment-driven |
| Docker multi-service stack | API + Postgres + frontend |
| Embedding model pre-cache in Docker | `fastembed` in production image |
| Audit log for AI actions | Implemented |
| Human review workflow | Implemented |
| Auth / RBAC | Not implemented — add before real deployment |
| Alembic migrations | Not implemented — use `create_all()` for demo |
| HIPAA / GDPR compliance | Not in scope for portfolio |

## Docker (recommended demo / staging)

```bash
docker compose up --build
```

| Service | URL | Notes |
|---------|-----|-------|
| Frontend | http://localhost:5173 | nginx → API proxy |
| API | http://localhost:8000 | 2 uvicorn workers |
| Postgres | localhost:5432 | pgvector image |

Production compose uses `fastembed` embeddings and readiness checks on the database.

## Environment variables (production)

```bash
MEDIMIND_ENVIRONMENT=production
MEDIMIND_DATABASE_URL=postgresql://user:pass@postgres:5432/hep_assist
MEDIMIND_EMBEDDING_PROVIDER=fastembed
MEDIMIND_CORS_ORIGINS=https://your-frontend.example.com
MEDIMIND_RATE_LIMIT_ENABLED=true
MEDIMIND_RATE_LIMIT_PER_MINUTE=120
MEDIMIND_AUTO_SEED_ON_STARTUP=false   # disable in real staging after first seed
```

## Demo workflow script (interview walkthrough)

```bash
./scripts/demo_workflow.sh http://127.0.0.1:8000
```

Runs 10 steps: health probes, safe Q&A, refusal demo, Amharic example, evaluation, audit.

## Cloud (Render)

See [RENDER_DEPLOY.md](RENDER_DEPLOY.md). Blueprint: [render.yaml](../render.yaml) with `/health/ready` probe.

## Screenshots

```bash
# Start API + frontend, then:
google-chrome --headless --screenshot=docs/screenshots/ask.png http://127.0.0.1:5173/ask
# Or: python scripts/capture_screenshots.py  (requires playwright)
```

## Before claiming “production” externally

1. Add authentication and role-based access (health worker vs reviewer vs admin)
2. Replace `create_all()` with Alembic migrations
3. Complete security review and penetration test
4. Legal/compliance review for target jurisdiction
5. Use real approved clinical content from authorized sources only
6. Remove or gate auto-seed in non-demo environments
