# GitHub Portfolio Status Report

**Profile:** https://github.com/dawit-Tegegnwork  
**Report date:** 2026-06-29  
**Overall level:** Strong mid-level portfolio — recruiter-ready for backend, healthcare integration, and application-support roles

---

## Executive summary

| Metric | Value |
|--------|-------|
| Public repos | 25 |
| Six pinned portfolio targets | Built, tested, pushed |
| Automated tests (6 pinned repos) | 46+ passing locally |
| CI workflows | All 6 pinned repos |
| Live portfolio site | https://dawit-tegegnwork.github.io/portfolio-website/ |
| Cloud API deploy | One-click Render blueprints (healthcare AI + enterprise workflow) |

**Your strongest narrative:** Backend engineer with digital health integration experience (OpenHIM, DHIS2, LIS) plus a complete set of role-targeted demos (AI workflow, RBAC, Go transactions, Firebase, CPIMS-style data quality, support runbooks).

---

## Six pinned portfolio repos

### 1. healthcare-ai-workflow-assistant

| | |
|---|---|
| **URL** | https://github.com/dawit-Tegegnwork/healthcare-ai-workflow-assistant |
| **Completion** | ~92% |
| **Tests** | 12 (pytest, CI on Python 3.12) |
| **What it does** | Synthetic clinical notes → mock LLM structured extraction → human review (approve/reject) → PostgreSQL/SQLite audit log + HTML dashboard |
| **Stack** | Python 3.12, FastAPI, SQLModel, Docker Compose, mock LLM |
| **Live deploy** | [Render one-click](docs/RENDER_DEPLOY.md) |
| **Role fit** | AI Focus Engineer, Backend, Healthcare IT |

### 2. enterprise-workflow-management-system

| | |
|---|---|
| **URL** | https://github.com/dawit-Tegegnwork/enterprise-workflow-management-system |
| **Completion** | ~88% |
| **Tests** | 7 (pytest) |
| **What it does** | JWT login, RBAC (admin/manager/staff/auditor), request submit → approve/reject workflow, audit log, dashboard counts, CSV export |
| **Stack** | Python 3.12, FastAPI, SQLModel, JWT, PostgreSQL/SQLite |
| **Live deploy** | [Render one-click](https://github.com/dawit-Tegegnwork/enterprise-workflow-management-system/blob/master/docs/RENDER_DEPLOY.md) |
| **Role fit** | Full Stack Backend, Enterprise/OVID-style workflow roles |

### 3. golang-transaction-api

| | |
|---|---|
| **URL** | https://github.com/dawit-Tegegnwork/golang-transaction-api |
| **Completion** | ~85% |
| **Tests** | 10 (Go unit + HTTP) |
| **What it does** | Wallet-style REST API: users, accounts, deposit/withdraw/transfer with idempotency keys, row locking, transaction history |
| **Stack** | Go 1.22, PostgreSQL, Docker Compose, SQLite for tests |
| **Role fit** | Golang Developer, Fintech/backend API roles |

### 4. node-firebase-mobile-backend

| | |
|---|---|
| **URL** | https://github.com/dawit-Tegegnwork/node-firebase-mobile-backend |
| **Completion** | ~80% |
| **Tests** | 3 (Firebase emulator integration) |
| **What it does** | Synthetic transport backend: Cloud Functions on trip status changes, Firestore security rules, emulator-first dev (no paid Firebase) |
| **Stack** | TypeScript, Firebase emulators, Cloud Functions v2 |
| **Role fit** | Mobile backend, Firebase, Safe Transport-style roles |

### 5. cpims-information-management-demo

| | |
|---|---|
| **URL** | https://github.com/dawit-Tegegnwork/cpims-information-management-demo |
| **Completion** | ~90% |
| **Tests** | 11 (pytest) |
| **What it does** | Synthetic case records with completeness scoring, duplicate detection, CSV import/export, data-quality CLI report |
| **Stack** | Python 3.12, FastAPI, SQLAlchemy, SQLite |
| **Role fit** | CPIMS, information management, data quality engineering |

### 6. application-support-runbook-lab

| | |
|---|---|
| **URL** | https://github.com/dawit-Tegegnwork/application-support-runbook-lab |
| **Completion** | ~85% |
| **Tests** | 6 (pytest) |
| **What it does** | Seven support runbooks (incident, UAT, release, SQL checks) + FastAPI ticket tracker with synthetic INC tickets |
| **Stack** | Markdown runbooks, Python, FastAPI, SQLite |
| **Role fit** | Application Support Manager, Healthcare IT support |

---

## Supporting hub repos

| Repo | What it does | Completion |
|------|--------------|------------|
| [dawit-tegegnwork](https://github.com/dawit-Tegegnwork/dawit-tegegnwork) | Profile README hub with featured projects, CI badges, live links | ~90% |
| [portfolio-website](https://github.com/dawit-Tegegnwork/portfolio-website) | React portfolio with 8 project cards | ~85% — [live](https://dawit-tegegnwork.github.io/portfolio-website/) |
| [healthcare-integration-portfolio](https://github.com/dawit-Tegegnwork/healthcare-integration-portfolio) | Index of all healthcare/integration demos | ~95% |

---

## Established healthcare repos (not in pin set)

| Repo | What it does | Level |
|------|--------------|-------|
| [echis-dhis2-mediator](https://github.com/dawit-Tegegnwork/echis-dhis2-mediator) | OpenHIM mediator: synthetic eCHIS reports → DHIS2 payloads | Strong |
| [lis-analyzer-integration-demo](https://github.com/dawit-Tegegnwork/lis-analyzer-integration-demo) | Lab analyzer CSV/JSON ingestion, validation, LIS payloads | Strong |
| [hospital-management-system](https://github.com/dawit-Tegegnwork/hospital-management-system) | WIP Ethiopian EMR scaffold (React, tRPC, MySQL) | WIP ~40% |
| [OpenELIS-Global-2](https://github.com/dawit-Tegegnwork/OpenELIS-Global-2) | Fork for ecosystem exploration | Fork signal |

---

## Role readiness matrix

| Target role | Best proof repos | Readiness |
|-------------|------------------|-----------|
| Backend Developer | healthcare-ai, enterprise-workflow, golang-transaction-api | **Strong** |
| Healthcare / Digital Health Engineer | echis-dhis2, lis-analyzer, healthcare-ai | **Strong** |
| AI Software Engineer | healthcare-ai-workflow-assistant | **Good** (mock LLM + human review) |
| Golang Developer | golang-transaction-api | **Good** |
| Firebase / Mobile Backend | node-firebase-mobile-backend | **Good** (emulator-first) |
| CPIMS / Info Management | cpims-information-management-demo | **Good** |
| Application Support | application-support-runbook-lab | **Good** |
| Full Stack | portfolio-website, hospital-management-system (WIP) | **Moderate** |

---

## cursoragent contributor

- Commit history rewritten; Contributors API shows only `dawit-Tegegnwork` on all six repos.
- GitHub sidebar cache may lag 24–72 hours. See [docs/CURSORAGENT_CONTRIBUTOR.md](CURSORAGENT_CONTRIBUTOR.md).
- Future commits will **not** include `Co-authored-by: Cursor`.

---

## Manual actions for you

1. **Pin six repos** on https://github.com/dawit-Tegegnwork → Customize pins (order in [docs/GITHUB_POLISH.md](GITHUB_POLISH.md)).
2. **Deploy to Render** (optional, free): click Deploy buttons in `RENDER_DEPLOY.md` for healthcare AI and enterprise workflow; add live URLs to profile when ready.
3. **Consider private:** `job-application-engine` (personal automation noise for recruiters).

---

## Test summary (local run 2026-06-29)

| Repo | Tests passed |
|------|--------------|
| healthcare-ai-workflow-assistant | 12 |
| enterprise-workflow-management-system | 7 |
| golang-transaction-api | 10 |
| node-firebase-mobile-backend | 3 |
| cpims-information-management-demo | 11 |
| application-support-runbook-lab | 6 |
| **Total** | **49** |

---

## Next optional upgrades

- Attach Render PostgreSQL for persistent cloud demos
- Expand Firebase rules unit tests
- Finish hospital-management-system EMR scaffold
- Add interview story doc per project (problem, stack, tradeoff, deploy)
