from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_conversation_service
from app.api.v1.dtos.chat import ChatRequest, ChatResponse
from app.api.v1.mappers import to_chat_response
from app.application.services.conversation_service import ConversationService

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse, summary="Send a message to the assistant")
async def chat(
    body: ChatRequest,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
) -> ChatResponse:
    reply = await service.chat(user_id=body.user_id, message=body.message)
    return to_chat_response(reply)
