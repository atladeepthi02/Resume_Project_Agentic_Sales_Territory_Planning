"""Correlation-ID based structured logging (PRD section 11/13)."""

from __future__ import annotations

import json
import logging
import time
import uuid
from contextvars import ContextVar
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("sales_agent_api")

CORRELATION_ID_HEADER = "X-Correlation-ID"
_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


def new_correlation_id() -> str:
    return uuid.uuid4().hex


def set_correlation_id(value: str) -> None:
    _correlation_id.set(value)


def get_correlation_id() -> str:
    return _correlation_id.get() or ""


def log_event(event: str, **fields: Any) -> None:
    """Emit a single structured log line carrying the correlation ID."""
    payload = {"event": event, "correlation_id": get_correlation_id(), **fields}
    logger.info(json.dumps(payload, default=str))


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Propagate or generate a correlation ID and log request outcomes."""

    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get(CORRELATION_ID_HEADER) or new_correlation_id()
        set_correlation_id(correlation_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:  # noqa: BLE001 - log then re-raise for the error handler
            log_event(
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
            )
            raise
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers[CORRELATION_ID_HEADER] = correlation_id
        log_event(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        return response
