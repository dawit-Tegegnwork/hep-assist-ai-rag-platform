# GitHub Portfolio Status Report

**Profile:** https://github.com/dawit-Tegegnwork  
**Updated:** 2026-06-29  
**Overall level:** Business-ready portfolio demos for backend, healthcare AI, digital health, and application support roles

---

## Executive summary

| Metric | Value |
|--------|-------|
| Pinned portfolio repos | 6 (functional + documented) |
| Total automated tests | 55+ passing locally |
| CI workflows | All 6 repos |
| Live portfolio site | https://dawit-tegegnwork.github.io/portfolio-website/ |
| Cloud deploy blueprints | healthcare-ai + enterprise-workflow (Render) |

---

## Business-ready scorecard

| Repo | Boot | Auto-seed | HTML UI | Demo flow | Tests |
|------|:----:|:---------:|:-------:|:---------:|:-----:|
| healthcare-ai-workflow-assistant | Yes | Yes | Dashboard | Yes | 12 |
| enterprise-workflow-management-system | Yes | Yes | Landing | Yes | 9 |
| golang-transaction-api | Yes | Yes | Landing | Yes | 10 |
| node-firebase-mobile-backend | Yes | Script | Emulator UI | Yes | 3 |
| cpims-information-management-demo | Yes | Yes | Dashboard | Yes | 12 |
| application-support-runbook-lab | Yes | Yes | Triage board | Yes | 7 |

---

## What changed (functional)

### healthcare-ai-workflow-assistant
- Auto-seed on app startup
- Postgres healthcheck in Docker Compose
- Dashboard shows note list + review status
- `GET /api/v1/notes` list endpoint
- Review action logging

### enterprise-workflow-management-system
- `GET /api/v1/requests` and `GET /api/v1/requests/{id}`
- `GET /api/v1/requests/{id}/history`
- Seeded demo workflow requests on startup
- Stricter reject/request_changes transitions
- Fixed CSV export route ordering
- Postgres healthcheck

### golang-transaction-api
- Auto-seed demo user + funded account
- `GET /audit` endpoint
- HTML landing page at `/`
- Sanitized internal error responses
- `.env.example`

### node-firebase-mobile-backend
- `npm run demo` one-command emulators
- `scripts/seed-emulator.ts` + `npm run seed:emulator`
- `.env.example`

### cpims-information-management-demo
- Fixed Docker Compose volume (data-only mount)
- `/dashboard` operations view
- Status lifecycle validation on PATCH
- Tests for invalid transitions

### application-support-runbook-lab
- Docker Compose + Dockerfile
- `/board` triage HTML UI
- `GET /api/tickets?ticket_number=INC-240601`
- `scripts/data_health_check.py`
- `.env.example`

### portfolio-website
- Project cards with screenshots, “What it proves” bullets, deploy links

---

## Per-repo descriptions

| Repo | What it does |
|------|----------------|
| **healthcare-ai-workflow-assistant** | Synthetic notes → mock LLM extraction → human review → audit log + dashboard |
| **enterprise-workflow-management-system** | JWT + RBAC approval workflows, audit trail, CSV export, seeded requests |
| **golang-transaction-api** | Go wallet API with idempotency, transfers, audit log, auto-seed |
| **node-firebase-mobile-backend** | Firebase emulator backend: Cloud Functions, Firestore rules, trip notifications |
| **cpims-information-management-demo** | Synthetic case records, completeness, duplicates, CSV, dashboard |
| **application-support-runbook-lab** | Support runbooks + triage board + ticket tracker API |

---

## Test results (local)

| Repo | Result |
|------|--------|
| healthcare-ai-workflow-assistant | 12 passed |
| enterprise-workflow-management-system | 9 passed |
| golang-transaction-api | 10 passed |
| node-firebase-mobile-backend | 3 passed (emulator) |
| cpims-information-management-demo | 12 passed |
| application-support-runbook-lab | 7 passed |

---

## Blocked / manual

1. **Pin six repos** on GitHub profile (Customize pins)
2. **Render live URLs** — click Deploy in each repo’s `RENDER_DEPLOY.md`
3. **cursoragent sidebar** — may take 24–72h to clear after history rewrite

---

## Recommended pin order

1. healthcare-ai-workflow-assistant  
2. enterprise-workflow-management-system  
3. golang-transaction-api  
4. node-firebase-mobile-backend  
5. cpims-information-management-demo  
6. application-support-runbook-lab  
