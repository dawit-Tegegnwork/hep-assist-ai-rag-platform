# Release Checklist

Use before tagging a release or deploying to staging/production-like environments.

**System:** eRIS Modernization Lab (synthetic)  
**Release discipline:** Stabilization-first — no deploy without smoke tests and rollback plan.

## Pre-release

- [ ] All CI checks green (`pytest`, frontend `lint`, `build`)
- [ ] `CHANGELOG` or release notes drafted (if applicable)
- [ ] `.env.example` reflects any new `MEDIMIND_*` variables
- [ ] Demo credentials documented in README (synthetic only)
- [ ] Database backup taken (if not fresh seed environment)
- [ ] Rollback plan reviewed: `docs/checklists/rollback.md`

## Automated verification

```bash
MEDIMIND_EMBEDDING_PROVIDER=mock PYTHONPATH=backend pytest -q
cd frontend && npm run lint && npm run build
```

## Smoke tests (API)

```bash
./scripts/demo_regulatory_workflow.sh http://127.0.0.1:8000
```

Expected: login, submit, review transitions, resubmit, approve — all HTTP 200.

## Smoke tests (UI)

| Step | URL | Expected |
|------|-----|----------|
| Health | `/health/ready` | `status: ready` |
| Login | `/login` | Sign in as `reviewer` |
| Applications | `/applications` | Dashboard counts visible |
| Audit | `/audit` | Events listed |

## Post-release

- [ ] Verify `/health/live` and `/health/ready` on target host
- [ ] Spot-check audit log for release-window activity
- [ ] Notify stakeholders of demo credential location (portfolio only)
- [ ] Monitor error logs for 15 minutes (see support runbook)

## Sign-off

| Role | Name | Date |
|------|------|------|
| Developer | | |
| Reviewer | | |
