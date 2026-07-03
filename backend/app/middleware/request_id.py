import time
import uuid
from collections import defaultdict
from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import get_settings


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 120) -> None:
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in {"/health", "/health/live", "/health/ready", "/docs", "/openapi.json"}:
            return await call_next(request)

        settings = get_settings()
        if not settings.rate_limit_enabled:
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - 60
        self._hits[client] = [t for t in self._hits[client] if t >= window_start]

        if len(self._hits[client]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again shortly."},
                headers={"Retry-After": "60"},
            )

        self._hits[client].append(now)
        return await call_next(request)
