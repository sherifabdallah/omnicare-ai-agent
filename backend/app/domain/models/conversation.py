"""Conversation-level value objects: what the assistant produces for one turn."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GuardrailVerdict(BaseModel):
    model_config = ConfigDict(frozen=True)

    blocked: bool
    reason: str | None = None

    @property
    def allowed(self) -> bool:
        return not self.blocked

    @classmethod
    def allow(cls) -> GuardrailVerdict:
        return cls(blocked=False)

    @classmethod
    def block(cls, reason: str) -> GuardrailVerdict:
        return cls(blocked=True, reason=reason)


class Citation(BaseModel):
    """A retrieved policy passage that backs an answer."""

    source: str
    section: str
    excerpt: str
    score: float = Field(ge=0.0, le=1.0)

    @property
    def label(self) -> str:
        return f"{self.source} — {self.section}"


class ToolInvocation(BaseModel):
    """A tool the agent called while answering."""

    name: str
    args: dict[str, Any]
    result: Any = None
    status: str = "success"


class AssistantReply(BaseModel):
    """The outcome of one conversational turn."""

    text: str
    citations: list[Citation] = Field(default_factory=list)
    tool_invocations: list[ToolInvocation] = Field(default_factory=list)
    blocked: bool = False

    @property
    def sources(self) -> list[str]:
        return [c.label for c in self.citations]
