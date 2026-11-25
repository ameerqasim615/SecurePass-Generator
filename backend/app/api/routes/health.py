from __future__ import annotations

from fastapi import APIRouter, Request

from app.schemas.system import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    """Liveness check used by the frontend status panel and Render's health probe."""
    settings = request.app.state.settings
    return HealthResponse(status="ok", service=settings.app_name, version=settings.app_version)
