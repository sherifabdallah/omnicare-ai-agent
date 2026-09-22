"""Data-transfer objects for the chat endpoints (the public wire contract)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(
        ...,
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_\-]+$",
        description="Stable identifier of the end user; used as the conversation thread.",
        examples=["usr_123"],
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The message to send to the assistant.",
        examples=["Is water damage from a burst pipe covered?"],
    )


class ToolCallDTO(BaseModel):
    name: str
    args: dict[str, Any]
    result: Any = None
    status: str = "success"


class CitationDTO(BaseModel):
    source: str
    section: str
    excerpt: str
    score: float = Field(ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    response: str
    sources: list[str] = Field(default_factory=list)
    tool_calls: list[ToolCallDTO] = Field(default_factory=list)
    citations: list[CitationDTO] = Field(default_factory=list)
    blocked: bool = Field(default=False, description="True when the input guardrail rejected the message.")
