# Support Runbook

**System:** eRIS Modernization Lab  
**Audience:** Developers, demo operators, portfolio reviewers  
**Severity definitions:** P1 = demo broken for interview; P2 = partial feature; P3 = docs/clarification

## Quick reference

| Check | Command / URL |
|-------|---------------|
| Liveness | `GET /health/live` |
| Readiness (DB) | `GET /health/ready` |
| API docs | `/docs` |
| Demo script | `./scripts/demo_regulatory_workflow.sh` |
| Tests | `MEDIMIND_EMBEDDING_PROVIDER=mock PYTHONPATH=backend pytest` |

## Demo credentials (synthetic)

| Username | Password | Role |
|----------|----------|------|
| applicant | applicant123 | Submit / resubmit |
| reviewer | reviewer123 | Technical review |
| admin | admin123 | Full access |
| auditor | auditor123 | Read-only |

## Common issues

### 401 on `/api/v1/regulatory/*`

**Cause:** Missing or expired Bearer token.  
**Fix:** `POST /api/v1/auth/login` with demo credentials; pass `Authorization: Bearer <token>`.

### 400 Invalid transition

**Cause:** Workflow state machine rejected action (e.g., approve from `submitted`).  
**Fix:** Follow valid path: `submitted` → `start_technical_review` → `approve`/`reject`/`request_clarification`. See `backend/app/regulatory/workflow.py`.

### 403 Role cannot perform action

**Cause:** RBAC enforcement — e.g., applicant attempting approve.  
**Fix:** Use correct demo account per `docs/DEMO_WALKTHROUGH.md`.

### Database not ready

**Symptom:** `/health/ready` returns 503.  
**Fix:**
```bash
docker compose ps
docker compose logs db api
# Ensure MEDIMIND_DATABASE_URL matches compose network
```

### Empty applications list

**Fix:** Seed synthetic data:
```bash
PYTHONPATH=backend python -m app.scripts.seed --force
```

### Audit log empty

**Cause:** Transitions performed without auth or DB unavailable (JSONL fallback).  
**Fix:** Confirm `MEDIMIND_DATABASE_URL` set; re-run workflow with authenticated calls.

## Log locations

| Environment | Location |
|-------------|----------|
| Docker Compose | `docker compose logs api` |
| Local uvicorn | stdout |
| Audit (no DB) | `MEDIMIND_AUDIT_LOG_PATH` (default `audit_logs.jsonl`) |

## Escalation (portfolio context)

This is a portfolio lab — escalation is to the repository maintainer:

1. Capture failing request (method, path, status, body)
2. Attach `pytest` output and `demo_regulatory_workflow.sh` output
3. File GitHub issue with reproduction steps

## Maintenance windows

For demo resets before interviews:

```bash
docker compose down -v   # destroys volumes — dev only
docker compose up --build
PYTHONPATH=backend python -m app.scripts.seed --force
```

## Related documents

- Release: `docs/checklists/release.md`
- Rollback: `docs/checklists/rollback.md`
- Migration: `docs/migration/gcp-to-local-plan.md`
- Assessment: `docs/legacy-modernization-assessment.md`
