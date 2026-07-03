# Legacy Modernization Assessment

**System:** Synthetic eRIS-style regulatory information system (portfolio lab)  
**Assessment date:** July 2026  
**Scope:** Application intake, technical review, clarification, approval/rejection, audit trail  
**Disclaimer:** This document describes a fictional legacy baseline and a synthetic modernization target. It is not an assessment of any real EFDA or government system.

## Executive summary

The legacy regulatory workflow platform exhibited typical symptoms of a long-lived monolith: manual queues, inconsistent role enforcement, sparse audit records, and release processes tied to a single cloud tenant. This modernization lab demonstrates a stabilized replacement pattern with explicit workflow states, role-based access, per-transition audit logging, and documented migration/release discipline.

## Legacy pain points (synthetic baseline)

| Area | Legacy behavior | Business impact |
|------|-----------------|-----------------|
| Application intake | Email/PDF attachments with manual ticket creation | Slow turnaround, lost documents |
| Technical review | Shared spreadsheet queue, no state machine | Reviewers overwrite each other's work |
| Clarification loop | Phone/email with no system record | Applicants resubmit without traceability |
| Auditability | Database updates without actor attribution | Compliance gaps during inspections |
| Role separation | Shared admin accounts | Applicants could access internal review notes |
| Migration | Single GCP project, manual VM snapshots | Risky releases, long rollback windows |

## Target modernization outcomes

1. **Stabilization** — Enforce valid state transitions server-side; reject invalid moves (e.g., approve before technical review).
2. **Regulatory workflow** — Model submitted → technical review → clarification → resubmit → decision with audit on every step.
3. **Role-based access** — Separate applicant, technical reviewer, admin, and auditor capabilities.
4. **Migration readiness** — Document GCP-to-local and containerized deployment paths; environment parity checklist.
5. **Release discipline** — Pre-release checklist, smoke tests, and rollback procedure.

## Current lab implementation mapping

| Legacy gap | Lab implementation |
|------------|-------------------|
| Manual review queue | `GET /api/v1/regulatory/applications` with status filters |
| Missing audit trail | `AuditEventRecord` + `GET /api/v1/regulatory/applications/{id}/audit` |
| Weak roles | JWT auth with `applicant`, `technical_reviewer`, `admin`, `auditor` |
| Invalid transitions | `validate_transition()` in `backend/app/regulatory/workflow.py` |
| Dashboard visibility | `GET /api/v1/regulatory/dashboard/summary` |

## Residual risks (honest)

- Alembic migrations not yet implemented (`create_all()` only)
- Demo credentials are hard-coded for portfolio use
- Legacy Q&A module remains open (unauthenticated) as a stabilized submodule
- No formal penetration test or production hardening

## Recommended next phase (if this were a real program)

1. Introduce Alembic migrations and versioned schema changes
2. Integrate with enterprise IdP (OIDC) instead of demo JWT users
3. Add document storage with checksum verification for dossier attachments
4. Wire observability (structured logs, metrics, alerting) per `docs/operations/support-runbook.md`
5. Execute pilot migration using `docs/migration/gcp-to-local-plan.md`

## References

- API: `docs/api.md`
- Release checklist: `docs/checklists/release.md`
- Rollback checklist: `docs/checklists/rollback.md`
- Support runbook: `docs/operations/support-runbook.md`
- Recruiter demo: `docs/DEMO_WALKTHROUGH.md`
