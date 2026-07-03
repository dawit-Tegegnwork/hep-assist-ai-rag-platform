# Interoperability Lab — Deployment Runbook

Operational guide for running Dawit's healthcare interoperability modernization lab locally or in Docker.

## Prerequisites

- Python 3.12+
- `pip install -r requirements-dev.txt`
- Optional: Docker + Docker Compose for full platform

## Local development (interop only)

```bash
cd /path/to/medimind-hep-assist-ai
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt

export MEDIMIND_DATABASE_URL=sqlite:///./interop_local.db
export MEDIMIND_AUTO_SEED_ON_STARTUP=false
export MEDIMIND_RATE_LIMIT_ENABLED=false

cd backend
PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify:

| Check | Command / URL |
|-------|----------------|
| Liveness | `curl http://localhost:8000/health/live` |
| Interop sources | `curl http://localhost:8000/api/v1/interop/sources` |
| Dashboard | http://localhost:8000/interop/dashboard |

## Docker (full stack)

```bash
docker compose up --build
```

Interop endpoints share the API service on port **8000**. PostgreSQL stores interop messages and audit events alongside the RAG platform tables.

Environment variables (see `.env.example`):

| Variable | Purpose |
|----------|---------|
| `MEDIMIND_DATABASE_URL` | SQLite (dev) or PostgreSQL (compose) |
| `MEDIMIND_RATE_LIMIT_ENABLED` | Set `false` for local demos |
| `MEDIMIND_AUTO_SEED_ON_STARTUP` | RAG seed; interop uses API samples |

## Demo script

```bash
chmod +x scripts/interop_demo.sh
./scripts/interop_demo.sh http://127.0.0.1:8000
```

Expected outcomes:

1. OpenMRS valid payload → `transformed`
2. OpenELIS, DHIS2, FHIR ingests succeed
3. Invalid OpenMRS payload → `validation_failed`
4. Duplicate OpenMRS ingest → HTTP 409
5. Dashboard shows message counts and audit events

## Running tests

```bash
PYTHONPATH=backend pytest tests/test_interop.py -q
```

Full suite:

```bash
PYTHONPATH=backend pytest -q
```

## Production cautions

This lab is a **portfolio demonstration**:

- Do not expose to the public internet without authentication
- Do not load real PHI
- Do not describe deployment as "connected to OpenMRS/OpenELIS/DHIS2"

For production-style hardening (future work, not required for demo):

- API keys or OAuth2 on ingest endpoints
- TLS termination
- Separate database schema per tenant
- Dead-letter queue for failed validations

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `409 duplicate_id` | Expected when re-ingesting same external id; use new sample or reset DB |
| Empty dashboard | Run `./scripts/interop_demo.sh` or manual ingests |
| Table missing | Restart API to trigger `init_db()` |
| SQLite locked | Use PostgreSQL via docker compose |

## Reset data

**SQLite:**

```bash
rm -f backend/interop_local.db backend/healthcare_ai.db
```

**Docker:**

```bash
docker compose down -v
docker compose up --build
```

## Related docs

- [interop-lab/README.md](../interop-lab/README.md)
- [interoperability-map.md](./interoperability-map.md)
