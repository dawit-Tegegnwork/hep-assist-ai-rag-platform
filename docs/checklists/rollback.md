# Rollback Checklist

Execute when a release causes failed smoke tests, data integrity issues, or elevated error rates.

**Target rollback window:** 30 minutes from cutover (adjust per environment policy).

## Decision criteria (any one triggers rollback)

- `/health/ready` fails persistently after deploy
- Regulatory workflow smoke script fails (`demo_regulatory_workflow.sh`)
- Audit events missing for transitions performed during verification
- Dashboard counts diverge from expected baseline after seed
- Unauthenticated access to protected regulatory endpoints

## Immediate actions

1. **Stop traffic** — revert load balancer / DNS to previous version
2. **Announce** — notify ops channel with release tag and symptom
3. **Preserve evidence** — export logs and DB snapshot before destructive steps

## Container rollback (Docker Compose)

```bash
# If using tagged images
docker compose down
git checkout <previous-tag>
docker compose up --build -d
./scripts/demo_regulatory_workflow.sh http://127.0.0.1:8000
```

## Database rollback

| Scenario | Action |
|----------|--------|
| Schema-only change | Restore pre-release `pg_dump` |
| Bad seed / test data | `PYTHONPATH=backend python -m app.scripts.seed --force` (dev only) |
| Partial migration | Restore dump; re-run alignment scripts |

```bash
pg_restore -h localhost -U medimind -d medimind --clean pre_release.dump
```

## Verification after rollback

- [ ] `./scripts/demo_regulatory_workflow.sh` passes
- [ ] `pytest tests/test_regulatory_workflow.py` passes against rolled-back build
- [ ] Audit trail shows no orphaned transitions during incident window
- [ ] Document incident in postmortem template (date, cause, fix)

## Post-rollback

- [ ] Root cause identified before re-attempting release
- [ ] Release checklist updated if gap found
- [ ] Re-deploy only after fix merged and CI green
