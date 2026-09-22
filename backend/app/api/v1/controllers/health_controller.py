from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app import __version__
from app.api.dependencies import get_app_settings
from app.api.v1.dtos.health import HealthResponse
from app.core.config import Settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Liveness / configuration check")
async def health(settings: Annotated[Settings, Depends(get_app_settings)]) -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version=__version__,
        llm_provider=settings.llm_provider,
        llm_model=settings.resolved_model,
    )
