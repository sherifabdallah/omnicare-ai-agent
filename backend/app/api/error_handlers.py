"""Map application/domain exceptions to HTTP responses in one place."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import AssistantUnavailableError
from app.domain.exceptions import DomainError

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AssistantUnavailableError)
    async def assistant_unavailable(request: Request, exc: AssistantUnavailableError) -> JSONResponse:
        # Provider details go to the server log, never to the client.
        logger.error("Assistant unavailable on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": "The assistant is temporarily unavailable. Please try again shortly."},
        )

    @app.exception_handler(DomainError)
    async def domain_error(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})
