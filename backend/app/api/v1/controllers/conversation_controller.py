from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.api.dependencies import get_conversation_service
from app.application.services.conversation_service import ConversationService

router = APIRouter(tags=["conversations"])


@router.delete(
    "/conversations/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Forget the conversation memory for a user",
)
async def reset_conversation(
    user_id: Annotated[str, Path(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_\-]+$")],
    service: Annotated[ConversationService, Depends(get_conversation_service)],
) -> None:
    await service.reset(user_id)
