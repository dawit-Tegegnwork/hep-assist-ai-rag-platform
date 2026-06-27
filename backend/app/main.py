from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="MediMind HEP Assist AI",
        version="0.1.0",
        description=(
            "Synthetic healthcare AI backend MVP for clinical text preprocessing, "
            "guideline retrieval, SOAP note drafting, and audit logging."
        ),
    )
    app.include_router(router, prefix=settings.api_prefix)

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok", "service": settings.service_name}

    return app


app = create_app()

