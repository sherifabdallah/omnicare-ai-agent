"""FastAPI dependency providers. Resolve services from the composition root
so controllers never construct their collaborators (Dependency Injection)."""

from __future__ import annotations

from fastapi import Request

from app.application.services.conversation_service import ConversationService
from app.core.config import Settings, get_settings


def get_conversation_service(request: Request) -> ConversationService:
    return request.app.state.container.conversation_service


def get_app_settings() -> Settings:
    return get_settings()
