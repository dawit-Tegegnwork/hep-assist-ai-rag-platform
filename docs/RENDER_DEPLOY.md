# Deploy to Render (free tier)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/dawit-Tegegnwork/healthcare-ai-workflow-assistant)

## One-click deploy

1. Click **Deploy to Render** above (or import this repo in the [Render dashboard](https://dashboard.render.com/)).
2. Render reads [`render.yaml`](render.yaml) and builds the Docker image.
3. After deploy, open `https://<your-service>.onrender.com/docs` for Swagger UI.
4. Seed demo data (optional — run locally against the service or use API to create notes):

```bash
curl -X POST https://<your-service>.onrender.com/api/v1/notes \
  -H 'Content-Type: application/json' \
  -d '{"title":"Demo note","body_text":"Synthetic patient note for portfolio demo."}'
```

## Environment variables

| Variable | Default | Notes |
|----------|---------|-------|
| `MEDIMIND_DATABASE_URL` | `sqlite:////tmp/healthcare_ai.db` | Ephemeral on free tier; fine for demo |
| `OPENAI_API_KEY` | unset | Mock LLM used when unset |

## Production notes

- Free tier services spin down after inactivity; first request may take ~30s.
- For persistent data, attach a Render PostgreSQL instance and set `MEDIMIND_DATABASE_URL`.
- Never use real patient data on any deployment.

## Health check

```bash
curl https://<your-service>.onrender.com/health
```

Expected: `{"status":"ok","service":"Healthcare AI Workflow Assistant"}`
