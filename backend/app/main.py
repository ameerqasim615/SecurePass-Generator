"""FastAPI application factory.

Run locally:  uvicorn app.main:app --reload --env-file .env
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.errors import (
    AppError,
    app_error_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.middleware.security_headers import SecurityHeadersMiddleware


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        # Interactive docs are only exposed outside production.
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None,
        openapi_url=None if settings.is_production else "/openapi.json",
    )
    app.state.settings = settings

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=False,  # auth uses Bearer tokens, not cookies
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
        max_age=600,
    )

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
