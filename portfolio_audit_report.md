# Portfolio Audit Report — Dawit Tegegnwork Wubale

**Date:** 2026-06-29  
**GitHub profile:** https://github.com/dawit-Tegegnwork  
**Auditor scope:** Public and private repo inventory, README quality, secrets scan, CV alignment, pin recommendations.

---

## 1. Executive summary

The profile already shows credible healthcare and backend work (`echis-dhis2-mediator`, `lis-analyzer-integration-demo`, `medimind-hep-assist-ai`, profile README). Gaps versus submitted CVs: no public repos yet for enterprise workflow/RBAC, Golang transactions, Firebase mobile backend, CPIMS-style information management, or application-support runbooks. Several public learning experiments dilute the professional narrative and should be unpinned (not made private without explicit approval).

**Priority actions:**
1. Complete and rename `medimind-hep-assist-ai` → `healthcare-ai-workflow-assistant`
2. Build five new target portfolio repos (see section 4)
3. Pin the six target repos; link supporting healthcare demos from profile README
4. Consider making `job-application-engine` private (personal automation; already flagged in repo description)

---

## 2. Repository inventory

| Repo | Visibility | Fork | Has README | Description quality | CV relevance |
|------|------------|------|------------|---------------------|--------------|
| `dawit-tegegnwork` | Public | No | Yes | Strong profile README | Profile hub |
| `medimind-hep-assist-ai` | Public | No | Yes | Good; MVP incomplete | AI + FastAPI + healthcare |
| `healthcare-integration-portfolio` | Public | No | Yes | Index repo | Digital health |
| `echis-dhis2-mediator` | Public | No | Yes | Strong | DHIS2/eCHIS, OpenHIM |
| `lis-analyzer-integration-demo` | Public | No | Yes | Strong | LIS, lab integration |
| `hospital-management-system` | Public | No | Yes | WIP labeled | EMR scaffold |
| `portfolio-website` | Public | No | Yes | Adequate | Portfolio |
| `devops-pipeline` | Public | No | Yes | Adequate | DevOps |
| `redash_bot` | Public | No | Yes | Adequate | Analytics automation |
| `OpenELIS-Global-2` | Public | Yes | Yes (upstream) | Fork signal | OpenELIS ecosystem |
| `redash-chatbot-add-on` | Public | Yes | Yes (upstream) | Fork | LLM add-on |
| `emr-module-demo` | Public | No | Yes | WIP | Healthcare |
| `pacs-dicom-workflow-tool` | Public | No | Yes | WIP | Healthcare imaging |
| `job-application-engine` | Public | No | Yes | Personal tooling | Low for recruiters |
| `ai-code-reviewer` | Public | No | Unknown | Experiment | Low |
| `alx-system_engineering-devops` | Public | No | Yes | Coursework | Low |
| `kuul` | Public | No | **No** | Empty | Unrelated |
| `fowl-farm-nexus` | Public | No | Yes | Unrelated domain | Unrelated |
| `microservices-platform` | Public | No | Yes | Learning | Low |
| `real-time-analytics` | Public | No | Yes | Learning | Low |
| 10+ private repos | Private | — | Mixed | Old coursework/duplicates | N/A |

**Total public repos:** 20

---

## 3. Secrets and sensitive data scan

| Check | Result |
|-------|--------|
| Local `medimind-hep-assist-ai` pattern scan (API keys, passwords) | No hardcoded secrets found |
| `.env.example` | Placeholder URLs only; safe |
| Docker Compose postgres password | Demo credential (`medimind/medimind`); acceptable for local portfolio |
| Employer/patient data in audited public repos | None observed in README/descriptions |
| `job-application-engine` | Flag for manual review before recruiter visits; consider private |

**Recommendation:** Never commit `.env`, production configs, or hospital screenshots. Keep synthetic data disclaimers in every healthcare repo.

---

## 4. Recommended six pinned repos (target end state)

| # | Repo | Status | Supports roles |
|---|------|--------|----------------|
| 1 | `healthcare-ai-workflow-assistant` | Rename from `medimind-hep-assist-ai` | AI Focus, Backend, Healthcare |
| 2 | `enterprise-workflow-management-system` | **To build** | Full Stack, Backend, OVID/Trust |
| 3 | `golang-transaction-api` | **To build** | Golang, Backend, Fintech |
| 4 | `node-firebase-mobile-backend` | **To build** | Safe Transport, Firebase |
| 5 | `cpims-information-management-demo` | **To build** | Plan CPIMS, Info management |
| 6 | `application-support-runbook-lab` | **To build** | Application Support, Healthcare IT |

**Keep public but not pinned:** `echis-dhis2-mediator`, `lis-analyzer-integration-demo`, `healthcare-integration-portfolio`, `OpenELIS-Global-2`

---

## 5. Repos to consider unpin / private later (requires Dawit approval)

Do **not** change visibility automatically.

| Repo | Reason |
|------|--------|
| `kuul` | No README; unrelated messaging experiment |
| `fowl-farm-nexus` | Unrelated to CV narrative |
| `microservices-platform` | Generic learning project |
| `real-time-analytics` | Generic learning project |
| `ai-code-reviewer` | Thin experiment |
| `alx-system_engineering-devops` | Coursework |
| `job-application-engine` | Personal automation; repo description says private recommended |

---

## 6. README cleanup candidates

| Repo | Action |
|------|--------|
| `kuul` | Add README or unpublish later |
| `emr-module-demo` | Add setup steps, synthetic data warning, WIP scope |
| `pacs-dicom-workflow-tool` | Same as above |
| `hospital-management-system` | Clarify demo credentials and non-production scope |

---

## 7. CV job target mapping

| Target role | Best current proof | Gap |
|-------------|-------------------|-----|
| Backend Developer | `medimind-hep-assist-ai`, `echis-dhis2-mediator` | Workflow persistence, RBAC sample |
| Full Stack Developer | `hospital-management-system`, `portfolio-website` | Enterprise workflow app |
| Software Engineer – AI Focus | `medimind-hep-assist-ai` (partial) | Human review loop, mock LLM |
| Golang Developer | — | Need `golang-transaction-api` |
| CPIMS / Info Management | — | Need `cpims-information-management-demo` |
| Application Support Manager | `devops-pipeline` (partial) | Need runbook lab |
| Firebase / Mobile Backend | — | Need `node-firebase-mobile-backend` |
| Digital Health / HIE | `echis-dhis2-mediator`, `lis-analyzer-integration-demo` | Strong |

---

## 8. Profile README gap analysis

**Current strengths:** Clear headline, experience section, tech stack table, featured projects, correct GitHub link.

**Gaps to address:**
- Headline should add: `AI & Backend Software Engineer | Digital Health Systems | APIs, PostgreSQL, FastAPI`
- Add six target portfolio projects as they ship
- Replace stale references to old GitHub username (`dawitwubale`) anywhere on the web
- Add grouped stack: Backend, AI, Digital Health, DevOps, Frontend
- Link `healthcare-integration-portfolio` as index of all demos

---

## 9. Local workspace notes

| Path | Notes |
|------|-------|
| `/home/dawit/medimind-hep-assist-ai` | Active Project 1 workspace; CI passing; Postgres unused for app data |
| Profile README | Lives in `dawit-tegegnwork` repo; draft update in `docs/profile_README_draft.md` |

---

## 10. Next steps (execution order)

1. ✅ This audit report
2. Update profile README draft
3. Complete healthcare AI workflow assistant (persistence, review, dashboard)
4. Build five new repos per 15-day plan
5. Update `portfolio-website` and pin repos on GitHub (after Dawit approves push)
