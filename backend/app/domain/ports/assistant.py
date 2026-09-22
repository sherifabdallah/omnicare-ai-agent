from __future__ import annotations

from typing import Protocol

from app.domain.models.conversation import AssistantReply


class Assistant(Protocol):
    """The conversational agent, independent of the framework that runs it."""

    async def chat(self, user_id: str, message: str) -> AssistantReply: ...

    async def reset(self, user_id: str) -> None: ...
