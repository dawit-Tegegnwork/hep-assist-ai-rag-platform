# GCP-to-Local Migration Plan

**Purpose:** Document how this modernization lab can be moved from a legacy GCP-hosted deployment to a local or on-prem container stack — a common Palladium/Data.FI-style stabilization scenario.

**Disclaimer:** Synthetic plan for portfolio demonstration. Not tied to any real government cloud tenant.

## Current state (legacy assumption)

| Component | Legacy GCP | Notes |
|-----------|------------|-------|
| App server | Compute Engine VM | Manual deploys via SSH |
| Database | Cloud SQL PostgreSQL | Nightly backup, no restore drill |
| Files | Cloud Storage bucket | Dossier PDFs outside DB |
| Secrets | VM metadata + `.env` on disk | Rotation manual |
| CI/CD | None / ad-hoc scripts | High release risk |

## Target state (this repo)

| Component | Local / container target |
|-----------|-------------------------|
| App | Docker Compose (`api` + `frontend` + `db`) |
| Database | PostgreSQL 16 with pgvector (Compose service) |
| Config | `.env` from `.env.example` |
| Audit | `audit_events` table + optional JSONL fallback |
| CI | GitHub Actions pytest + frontend build |

## Migration phases

### Phase 0 — Discovery (1 week)

- [ ] Inventory GCP resources (VM, Cloud SQL, buckets, firewall rules)
- [ ] Export schema DDL and row counts from production-like staging
- [ ] Map service accounts and secret dependencies
- [ ] Confirm regulatory workflow states in use vs. documented SOP

### Phase 1 — Parity environment (1–2 weeks)

```bash
# Clone repo and stand up local stack
git clone <repo-url> eris-modernization-lab
cd eris-modernization-lab
cp .env.example .env
docker compose up --build
```

- [ ] Run `PYTHONPATH=backend python -m app.scripts.seed` on empty DB
- [ ] Execute `./scripts/demo_regulatory_workflow.sh` — all steps pass
- [ ] Compare API response shapes with legacy system (OpenAPI export)

### Phase 2 — Data migration (synthetic approach)

For a real migration, typical steps:

1. **Freeze writes** on legacy system (maintenance window)
2. **Dump PostgreSQL** from Cloud SQL:
   ```bash
   pg_dump -h <cloud-sql-host> -U <user> -d eris -Fc -f eris_legacy.dump
   ```
3. **Restore to target**:
   ```bash
   pg_restore -h localhost -U medimind -d medimind eris_legacy.dump
   ```
4. **Run schema alignment** — map legacy status codes to `ApplicationStatus` enum
5. **Backfill audit** — one synthetic `regulatory.application.submit` per imported row if legacy lacked audit

This lab seeds synthetic data instead; see `backend/app/scripts/seed.py`.

### Phase 3 — Cutover

| Step | Owner | Verification |
|------|-------|--------------|
| DNS / load balancer switch | Infra | `/health/ready` returns 200 |
| Smoke test regulatory flow | App team | `demo_regulatory_workflow.sh` |
| Dashboard counts | QA | Summary matches expected seed |
| Rollback decision window | Release mgr | 30 min per `docs/checklists/rollback.md` |

### Phase 4 — Decommission GCP (after soak)

- [ ] 30-day read-only archive of Cloud SQL backup
- [ ] Revoke service account keys
- [ ] Document final state in change record

## Environment variable mapping

| Legacy (GCP VM) | Modern lab (`.env`) |
|-----------------|---------------------|
| `DATABASE_URL` | `MEDIMIND_DATABASE_URL` |
| `JWT_SECRET` | `MEDIMIND_AUTH_SECRET_KEY` |
| `CORS_ORIGINS` | `MEDIMIND_CORS_ORIGINS` |
| N/A | `MEDIMIND_AUTH_ENABLED=true` |

## Rollback trigger

If post-cutover error rate exceeds threshold or audit integrity check fails, execute `docs/checklists/rollback.md` within the agreed window.

## Local test commands

```bash
MEDIMIND_EMBEDDING_PROVIDER=mock PYTHONPATH=backend pytest tests/test_regulatory_workflow.py -v
docker compose up --build -d
./scripts/demo_regulatory_workflow.sh http://127.0.0.1:8000
```
