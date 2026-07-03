# 5-Minute Recruiter Demo Walkthrough

**System:** eRIS Modernization Lab (synthetic — not real eRIS, not connected to EFDA)

## Demo credentials

| Username | Password | Use in demo |
|----------|----------|-------------|
| `reviewer` | `reviewer123` | Primary walkthrough account |
| `applicant` | `applicant123` | Resubmit after clarification |
| `admin` | `admin123` | Optional — full access |
| `auditor` | `auditor123` | Read-only audit verification |

## Prerequisites

```bash
docker compose up --build
# Frontend: http://localhost:5173
# API: http://localhost:8000/docs
```

## Minute 0–1: Context and health

1. Open http://localhost:5173 — read home page modernization story
2. Confirm API: http://localhost:8000/health/ready → `"status": "ready"`
3. Talking point: *"This is a stabilization lab for legacy regulatory workflows — enforced states, RBAC, audit on every transition."*

## Minute 1–2: Reviewer queue

1. Go to http://localhost:5173/login
2. Sign in: `reviewer` / `reviewer123`
3. Open **Applications** — note dashboard counts (submitted, in review, clarification, approved)
4. Open **ERIS-DEMO-00002** (clarification requested) or any `submitted` application

**API equivalent:**
```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"reviewer","password":"reviewer123"}' | jq -r .access_token)
curl -s http://127.0.0.1:8000/api/v1/regulatory/dashboard/summary \
  -H "Authorization: Bearer $TOKEN" | jq
```

## Minute 2–3: Technical review transition

1. On a `submitted` application, click **Start technical review**
2. Click **Request clarification** with comment: *"Provide stability appendix"*
3. Show **Audit trail** section updating on the same page

**API:**
```bash
# Replace APP_ID
curl -X POST http://127.0.0.1:8000/api/v1/regulatory/applications/$APP_ID/transition \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action":"start_technical_review","comment":"Demo review"}'
```

## Minute 3–4: Applicant resubmit

1. Sign out → sign in as `applicant` / `applicant123`
2. Open the same application → **Resubmit with updates**
3. Sign out → sign in as `reviewer` → **Resume technical review** → **Approve**

**API:**
```bash
APPLICANT_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"applicant","password":"applicant123"}' | jq -r .access_token)
curl -X POST http://127.0.0.1:8000/api/v1/regulatory/applications/$APP_ID/resubmit \
  -H "Authorization: Bearer $APPLICANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dossier_summary":"Updated dossier with stability appendix.","applicant_note":"Addressed clarification"}'
```

## Minute 4–5: Audit and documentation

1. Open http://localhost:5173/audit — global audit events
2. On application detail — per-application audit trail
3. Mention docs: `docs/legacy-modernization-assessment.md`, release/rollback checklists

**Automated full script:**
```bash
./scripts/demo_regulatory_workflow.sh http://127.0.0.1:8000
```

## Endpoints to test (checklist)

| Method | Endpoint | Auth | Role |
|--------|----------|------|------|
| POST | `/api/v1/auth/login` | No | — |
| GET | `/api/v1/auth/me` | Yes | any |
| POST | `/api/v1/regulatory/applications` | Yes | applicant |
| GET | `/api/v1/regulatory/applications` | Yes | any |
| GET | `/api/v1/regulatory/applications/{id}` | Yes | any |
| POST | `/api/v1/regulatory/applications/{id}/transition` | Yes | reviewer/admin |
| POST | `/api/v1/regulatory/applications/{id}/resubmit` | Yes | applicant |
| GET | `/api/v1/regulatory/dashboard/summary` | Yes | reviewer/admin/auditor |
| GET | `/api/v1/regulatory/applications/{id}/audit` | Yes | any (own app for applicant) |
| GET | `/api/v1/audit` | No | legacy module |

## UI pages

| Page | URL |
|------|-----|
| Home | http://localhost:5173/ |
| Login | http://localhost:5173/login |
| Applications | http://localhost:5173/applications |
| Application detail | http://localhost:5173/applications/{id} |
| Audit log | http://localhost:5173/audit |
| Legacy Q&A | http://localhost:5173/ask |

## Closing talking points

- **Stabilization:** Invalid transitions rejected server-side with tests
- **Migration readiness:** Documented GCP-to-local plan
- **Release discipline:** Checklists for release and rollback
- **Honest scope:** Synthetic data; not a government system
