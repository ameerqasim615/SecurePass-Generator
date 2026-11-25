"""Consistent JSON error responses.

Every error leaves the API in one shape:

    {"error": {"code": "...", "message": "...", "details": [{"field": "...", "message": "..."}]}}

Unhandled exceptions are logged server-side and returned as a generic 500 so
internal details (stack traces, SQL, secrets) never reach the client. Validation
errors report field paths and messages but never echo the submitted values.
"""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

_REQUEST_SOURCES = {"body", "query", "path", "header", "cookie"}


class AppError(Exception):
    """Raise from services/routes to return a controlled error to the client."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def _envelope(code: str, message: str, details: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if details:
        error["details"] = details
    return {"error": error}


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope(exc.code, exc.message, exc.details),
    )


async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    try:
        phrase = HTTPStatus(exc.status_code).phrase
    except ValueError:
        phrase = "Error"
    message = exc.detail if isinstance(exc.detail, str) else phrase
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope(f"http_{exc.status_code}", message),
        headers=exc.headers,
    )


async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    details: list[dict[str, Any]] = []
    for err in exc.errors():
        loc = list(err.get("loc", ()))
        if loc and loc[0] in _REQUEST_SOURCES:
            loc = loc[1:]
        details.append(
            {
                "field": ".".join(str(part) for part in loc) or "(root)",
                "message": str(err.get("msg", "Invalid value")),
            }
        )
    return JSONResponse(
        status_code=422,
        content=_envelope("validation_error", "Request validation failed", details),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content=_envelope("internal_error", "An unexpected error occurred."),
    )
