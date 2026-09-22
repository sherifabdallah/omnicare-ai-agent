"""Domain -> DTO mapping. Keeps the wire format independent of domain models."""

from __future__ import annotations

from app.api.v1.dtos.chat import ChatResponse, CitationDTO, ToolCallDTO
from app.domain.models.conversation import AssistantReply


def to_chat_response(reply: AssistantReply) -> ChatResponse:
    return ChatResponse(
        response=reply.text,
        sources=reply.sources,
        tool_calls=[ToolCallDTO.model_validate(t.model_dump()) for t in reply.tool_invocations],
        citations=[CitationDTO.model_validate(c.model_dump()) for c in reply.citations],
        blocked=reply.blocked,
    )
