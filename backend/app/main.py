from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from app.api.interop import router as interop_router
from app.api.qa import router as qa_router
from app.api.routes import router
from app.api.workflow import router as workflow_router
from app.auth.router import router as auth_router
from app.regulatory.api import router as regulatory_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.health import build_health_payload, check_database
from app.db.session import init_db
from app.landing import render_landing
from app.middleware.logging import RequestLoggingMiddleware, configure_logging
from app.middleware.request_id import RateLimitMiddleware, RequestIdMiddleware
from app.scripts.seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level)
    init_db()
    if settings.auto_seed_on_startup:
        seed(force=False)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Community Health AI Modernization Lab",
        version=settings.app_version,
        description=(
            "Synthetic community-health modernization lab with safe AI guidance, "
            "interoperability adapters, role-based workflows, audit trails, and "
            "legacy-system stabilization patterns. Portfolio reference implementation only."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    register_exception_handlers(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit_per_minute)
    app.add_middleware(RequestIdMiddleware)

    app.include_router(auth_router, prefix=settings.api_prefix, tags=["auth"])
    app.include_router(regulatory_router, prefix=settings.api_prefix, tags=["regulatory"])
    app.include_router(router, prefix=settings.api_prefix, tags=["legacy"])
    app.include_router(workflow_router, prefix=settings.api_prefix, tags=["workflow"])
    app.include_router(qa_router, prefix=settings.api_prefix, tags=["qa"])
    app.include_router(interop_router, prefix=settings.api_prefix)

    @app.get("/health", tags=["ops"])
    def health_check() -> dict[str, object]:
        return build_health_payload(detailed=True)

    @app.get("/health/live", tags=["ops"])
    def liveness() -> dict[str, str]:
        return {"status": "ok", "service": settings.service_name}

    @app.get("/health/ready", tags=["ops"])
    def readiness() -> JSONResponse:
        db_ok, db_status = check_database()
        payload = {
            "status": "ready" if db_ok else "not_ready",
            "database": db_status,
        }
        return JSONResponse(status_code=200 if db_ok else 503, content=payload)

    @app.get("/", response_class=HTMLResponse, tags=["ui"])
    def landing_page() -> str:
        return render_landing(
            "Community Health AI Modernization Lab",
            "Synthetic modernization reference for health-worker AI, interoperability adapters, audit trails, and role-based workflow stabilization.",
            "Synthetic data only. Not medical advice. Not connected to any real hospital, ministry, EFDA, or patient system.",
            "hep-assist-ai-rag-platform",
            extra_links=[
                (settings.frontend_url, "React app"),
                ("/dashboard", "Legacy review dashboard"),
                ("/interop/dashboard", "Interop lab dashboard"),
            ],
            quick_steps=[
                'Check <a href="/health">/health</a> and <a href="/health/ready">/health/ready</a>',
                f'Open <a href="{settings.frontend_url}">React frontend</a> — AI guidance, interop, and workflow modules',
                'Interop lab: <a href="/interop/dashboard">/interop/dashboard</a> · <code>./scripts/interop_demo.sh</code>',
                'Login: <code>POST /api/v1/auth/login</code> (see README demo credentials)',
                'Submit application: <code>POST /api/v1/regulatory/applications</code>',
                'Review transitions: <code>POST /api/v1/regulatory/applications/{{id}}/transition</code>',
            ],
        )

    @app.get("/dashboard", response_class=HTMLResponse, tags=["ui"])
    def dashboard() -> str:
        template_path = Path(__file__).parent / "static" / "dashboard.html"
        return template_path.read_text(encoding="utf-8")

    @app.get("/interop/dashboard", response_class=HTMLResponse, tags=["ui"])
    def interop_dashboard() -> str:
        template_path = Path(__file__).parent / "static" / "interop_dashboard.html"
        return template_path.read_text(encoding="utf-8")

    return app


app = create_app()
