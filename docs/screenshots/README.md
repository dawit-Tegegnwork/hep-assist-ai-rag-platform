# Screenshots

Add demo screenshots here after running the app locally:

- `dashboard.png` — `/dashboard` review counts
- `swagger.png` — `/docs` OpenAPI UI
- `workflow.png` — note → extract → review curl or UI flow

Generate with browser screenshots or:

```bash
docker compose up --build
PYTHONPATH=backend python -m app.scripts.seed
# Open http://127.0.0.1:8000/dashboard and capture
```
