"""Use case: one conversational turn with the assistant.

Thin on purpose: the application boundary where auditing, metrics or
authorisation would live. The heavy lifting is behind the Assistant port.
"""

from __future__ import annotations

import logging

from app.domain.models.conversation import AssistantReply
from app.domain.ports.assistant import Assistant

logger = logging.getLogger(__name__)


class ConversationService:
    def __init__(self, assistant: Assistant) -> None:
        self._assistant = assistant

    async def chat(self, user_id: str, message: str) -> AssistantReply:
        reply = await self._assistant.chat(user_id, message)
        logger.info(
            "turn user=%s blocked=%s tools=%s citations=%d",
            user_id,
            reply.blocked,
            [t.name for t in reply.tool_invocations],
            len(reply.citations),
        )
        return reply

    async def reset(self, user_id: str) -> None:
        await self._assistant.reset(user_id)
        logger.info("conversation reset user=%s", user_id)
