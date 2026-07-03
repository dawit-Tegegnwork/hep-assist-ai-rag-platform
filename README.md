# Community Health AI Modernization Lab

Production-style **modernization lab** for community-health software: safe AI guidance over approved content, interoperability adapters, role-based workflows, audit trails, and release-ready documentation. Uses **synthetic data only**. This is **not** medical advice and is **not** connected to any real hospital, ministry, EFDA, or patient system.

[![Tests](https://github.com/dawit-Tegegnwork/hep-assist-ai-rag-platform/actions/workflows/test.yml/badge.svg)](https://github.com/dawit-Tegegnwork/hep-assist-ai-rag-platform/actions/workflows/test.yml)

**Target roles:** Healthcare AI Engineer, Digital Health Software Engineer, Health Interoperability Engineer, Backend Software Engineer.

## What this is (honest framing)

This repo demonstrates how existing-style health workflows can be **modernized** without pretending to replace real national systems. It is a **portfolio reference implementation** with:

- Health-worker AI guidance over approved synthetic content
- Retrieval-augmented answers with citations, refusal gates, and human review
- Interoperability adapters inspired by OpenMRS, OpenELIS, DHIS2, and FHIR-style payloads
- Role-based workflow module with server-side transition validation and audit trails
- Documented release, rollback, support, safety, and offline-first procedures
- Tests, Docker, screenshots, and demo scripts for recruiter/interview walkthroughs

## Legacy modernization story

### What legacy health systems often struggle with

| Pain point | Legacy behavior |
|------------|-----------------|
| Health guidance | PDF/manual knowledge, hard to search quickly |
| AI safety | Open-ended chat with no grounding or review |
| Interoperability | Inconsistent patient, lab, and reporting payloads |
| Auditability | Updates without actor, reason, or traceable decision |
| Role separation | Shared accounts or unclear responsibilities |
| Deployment | Manual releases, weak smoke tests, slow rollback |

### What this lab improves

| Capability | Implementation |
|------------|----------------|
| Safe AI guidance | RAG over approved synthetic content with citations |
| Safety controls | Emergency/diagnosis/prescribing refusal gates |
| Human review | approve / reject / request changes before trusting AI output |
| Interoperability | OpenMRS/OpenELIS/DHIS2/FHIR-inspired validation and export adapters |
| Workflow stabilization | Invalid transitions rejected with tests |
| Audit trail | question, answer, review, integration, and workflow events |
| Release discipline | `docs/checklists/release.md`, `docs/checklists/rollback.md`, support runbooks |

See [docs/legacy-modernization-assessment.md](docs/legacy-modernization-assessment.md) for the full assessment.

## Quick start (3 minutes)

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| React frontend | http://localhost:5173 |
| FastAPI + OpenAPI | http://localhost:8000/docs |
| Health (ready) | http://localhost:8000/health/ready |

### Demo credentials for workflow module (synthetic)

| Username | Password | Role |
|----------|----------|------|
| `applicant` | `applicant123` | Submit and resubmit applications |
| `reviewer` | `reviewer123` | Technical review and decisions |
| `admin` | `admin123` | Full workflow access |
| `auditor` | `auditor123` | Read-only audit access |

### 5-minute recruiter walkthrough

1. Open http://localhost:5173 — review the health AI modernization overview
2. Ask a safe health-worker question — verify citations and pending review
3. Ask an unsafe prescribing/diagnosis question — verify refusal
4. Run **Evaluation** — see synthetic golden-case pass/fail scoring
5. Open `/interop/dashboard` — validate and export synthetic health payloads
6. Optional workflow module: sign in as `reviewer` / `reviewer123` and review application transitions

Full script: [docs/DEMO_WALKTHROUGH.md](docs/DEMO_WALKTHROUGH.md)

```bash
chmod +x scripts/demo_regulatory_workflow.sh
./scripts/demo_regulatory_workflow.sh http://127.0.0.1:8000
```

### Local development

**Backend:**

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
export MEDIMIND_EMBEDDING_PROVIDER=mock
PYTHONPATH=backend uvicorn main:app --app-dir backend --reload
```

**Frontend:**

```bash
cd frontend && npm install && npm run dev
```

### Seed synthetic data

```bash
PYTHONPATH=backend python -m app.scripts.seed
# Reseed: PYTHONPATH=backend python -m app.scripts.seed --force
```

### Run tests

```bash
MEDIMIND_EMBEDDING_PROVIDER=mock PYTHONPATH=backend pytest
cd frontend && npm run lint && npm run build
```

## Architecture

```mermaid
flowchart TB
  subgraph frontend [ReactFrontend]
    Login[LoginRBAC]
    Apps[ApplicationsQueue]
    AuditUI[AuditLog]
    LegacyQA[LegacyQAModule]
  end

  subgraph api [FastAPI]
    Auth["/auth/login"]
    Reg["/regulatory/applications"]
    Dash["/regulatory/dashboard/summary"]
    AuditAPI["/audit"]
    QA["/questions legacy"]
  end

  subgraph data [PostgreSQL_or_SQLite]
    AppsDB[regulatory_applications]
    AuditDB[audit_events]
  end

  frontend --> api
  Reg --> AppsDB
  Reg --> AuditDB
  Auth --> Reg
```

See [docs/architecture.md](docs/architecture.md), [docs/api.md](docs/api.md), and [docs/operations/support-runbook.md](docs/operations/support-runbook.md).

## Regulatory workflow API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/login` | No | Obtain JWT |
| GET | `/api/v1/auth/me` | Yes | Current user |
| POST | `/api/v1/regulatory/applications` | applicant | Submit application |
| GET | `/api/v1/regulatory/applications` | Yes | List applications |
| GET | `/api/v1/regulatory/applications/{id}` | Yes | Application detail |
| POST | `/api/v1/regulatory/applications/{id}/transition` | reviewer | State transition |
| POST | `/api/v1/regulatory/applications/{id}/resubmit` | applicant | Resubmit after clarification |
| GET | `/api/v1/regulatory/dashboard/summary` | reviewer/auditor | Status counts |
| GET | `/api/v1/regulatory/applications/{id}/audit` | Yes | Per-application audit trail |
| GET | `/api/v1/audit` | No | Global audit log (legacy) |

### Example workflow (curl)

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"applicant","password":"applicant123"}' | jq -r .access_token)

curl -X POST http://127.0.0.1:8000/api/v1/regulatory/applications \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Synthetic Product XR-200",
    "application_type": "marketing_authorization",
    "applicant_organization": "Synthetic Pharma Ltd",
    "dossier_summary": "Demo dossier for regulatory workflow testing with sufficient detail."
  }'
```

## HEP Assist AI — health-worker guidance with safe AI layer

**Target role:** Senior AI Engineer (Last Mile Health / HEP Assist AI-style) — RAG, safety, human review, low-connectivity and local-language design.

This module shows **AI modernization layered on existing health-worker guidance** — not an open-ended chatbot. Community health workers already follow approved protocols; the demo adds retrieval and generation on that content only.

| Pattern | Implementation |
|---------|----------------|
| **Approved-content-only answers** | Vector RAG over indexed synthetic guidelines; refuse when retrieval confidence is low |
| **Citations** | Chunk title, excerpt, retrieval score on every grounded answer |
| **Human-in-the-loop review** | Approve / reject / request changes before trusting output |
| **Safety refusal** | Emergency, diagnosis, prescribing blocked pre-generation |
| **Risk & hallucination flags** | Rule-based + grounding heuristic (mock LLM path) |
| **Audit trail** | `qa.question.create`, `qa.answer`, `qa.answer.review`, `evaluation.run` |
| **Golden evaluation** | Pass/fail scoring on synthetic cases |
| **Amharic examples** | Architecture demo — **not** certified translation or full multilingual production |

**Honest framing:** Portfolio reference implementation. **Synthetic data only.** **Mock LLM by default.** Not medical advice.

### HEP Assist quick demo

```bash
./scripts/demo_workflow.sh http://127.0.0.1:8000
```

| UI | URL |
|----|-----|
| Ask question | http://localhost:5173/ask |
| Review queue | http://localhost:5173/review |
| Evaluation | http://localhost:5173/evaluation |
| Audit log | http://localhost:5173/audit |

Full walkthrough: [docs/interview-demo-script.md](docs/interview-demo-script.md)

### HEP Assist API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/questions` | Submit health-worker question |
| POST | `/api/v1/questions/{id}/answer` | RAG + safety + LLM (citations if grounded) |
| POST | `/api/v1/answers/{id}/review` | Human review action |
| POST | `/api/v1/evaluation/run` | Golden set with pass/fail |
| GET | `/api/v1/dashboard/qa-summary` | Q&A review counts |
| GET | `/api/v1/audit` | Global audit log |

### HEP Assist documentation

| Document | Purpose |
|----------|---------|
| [ai-safety-case.md](docs/ai-safety-case.md) | Safety gates, refusal reasons, human review |
| [rag-evaluation-plan.md](docs/rag-evaluation-plan.md) | Golden set, metrics, pass/fail rules |
| [offline-first-design.md](docs/offline-first-design.md) | Low-connectivity architecture notes |
| [local-language-support.md](docs/local-language-support.md) | Amharic examples, honest limitations |
| [deployment-runbook.md](docs/deployment-runbook.md) | Deploy, smoke tests, rollback |
| [interview-demo-script.md](docs/interview-demo-script.md) | 10-minute recruiter walkthrough |

### Screenshots (HEP Assist module)

| Home | Ask | Answer + citations |
|------|-----|-------------------|
| ![Home](docs/screenshots/home.png) | ![Ask](docs/screenshots/ask.png) | ![Answer](docs/screenshots/answer.png) |

| Review | Evaluation | Audit |
|--------|------------|-------|
| ![Review](docs/screenshots/review.png) | ![Evaluation](docs/screenshots/evaluation.png) | ![Audit](docs/screenshots/audit.png) |

Recapture: `python scripts/capture_screenshots.py` (stack running).

## Documentation index

| Document | Purpose |
|----------|---------|
| [ai-safety-case.md](docs/ai-safety-case.md) | Safe AI design and risk controls |
| [rag-evaluation-plan.md](docs/rag-evaluation-plan.md) | RAG evaluation approach |
| [offline-first-design.md](docs/offline-first-design.md) | Low-connectivity design thinking |
| [local-language-support.md](docs/local-language-support.md) | Amharic/local-language support scope |
| [interoperability-map.md](docs/interoperability-map.md) | OpenMRS/OpenELIS/DHIS2/FHIR-inspired adapters |
| [legacy-modernization-assessment.md](docs/legacy-modernization-assessment.md) | Legacy pain points vs. lab improvements |
| [checklists/release.md](docs/checklists/release.md) | Pre/post release checklist |
| [checklists/rollback.md](docs/checklists/rollback.md) | Rollback procedure |
| [operations/support-runbook.md](docs/operations/support-runbook.md) | Common issues and fixes |
| [DEMO_WALKTHROUGH.md](docs/DEMO_WALKTHROUGH.md) | Recruiter demo path |

## What this proves for recruiters

**Health-system modernization lab**

- **Legacy workflow improvement** — state machine, clarification loop, decision audit
- **Interoperability thinking** — validation, transformation, export, and audit
- **Stabilization** — RBAC, invalid transition rejection, tested dashboard counts
- **Release discipline** — checklists, smoke scripts, support runbook

**HEP Assist AI module (Last Mile Health / Senior AI Engineer)**

- RAG over **existing approved content**, not free-form medical chat
- Healthcare safety: refusal gates, approved-content-only mode, audit trails
- Human-in-the-loop AI before field use
- Low-connectivity and local-language **design thinking** with honest scope
- Testing: citations, refusal, review, audit, evaluation pass/fail

## Known limitations

| Area | Current state | Next step |
|------|---------------|-----------|
| Auth | Demo JWT users | Enterprise OIDC / IdP |
| Migrations | `create_all()` | Alembic |
| Document storage | Filename list only | Object store + checksums |
| Legacy Q&A | Open endpoints; mock LLM default | Auth alignment; production embeddings |
| HEP Assist eval | Golden set pass/fail on synthetic cases | Clinician-labeled eval harness |
| Compliance | Portfolio disclaimers | Formal assessment for real deployment |

## License

MIT — synthetic demo data only.
