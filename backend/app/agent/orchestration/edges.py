"""Routing functions (conditional edges)."""

from __future__ import annotations

from typing import Literal

from langgraph.graph import END
from langgraph.prebuilt import tools_condition

from app.agent.orchestration.state import AgentState


def route_after_guardrail(state: AgentState) -> Literal["agent", "__end__"]:
    return END if state["guardrail"]["blocked"] else "agent"


# Re-exported so the builder only depends on this module for routing.
route_after_agent = tools_condition
