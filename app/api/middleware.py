"""Request ID and rate limiting middleware."""

import time
import uuid
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.logging import request_id_ctx

# Simple in-memory rate limiter: {ip: [(timestamp, ...)]}
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT = 30  # requests
_RATE_WINDOW = 60  # seconds


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to every request and log record."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        token = request_id_ctx.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_ctx.reset(token)

        response.headers["X-Request-ID"] = request_id
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter by client IP."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()

        timestamps = _rate_limit_store[client_ip]
        # Remove expired entries
        _rate_limit_store[client_ip] = [t for t in timestamps if now - t < _RATE_WINDOW]

        if len(_rate_limit_store[client_ip]) >= _RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
            )

        _rate_limit_store[client_ip].append(now)
        return await call_next(request)
