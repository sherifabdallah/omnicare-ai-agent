"""Graph state shared by all nodes."""

from __future__ import annotations

from typing import TypedDict

from langgraph.graph import MessagesState


class GuardrailState(TypedDict):
    blocked: bool
    reason: str | None


class AgentState(MessagesState):
    """`messages` (with the add/remove reducer) plus the latest guardrail verdict."""

    guardrail: GuardrailState
