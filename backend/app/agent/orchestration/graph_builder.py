"""Assemble the LangGraph workflow (Builder pattern).

START -> guardrail --(blocked)--> END
             |
          (allowed)
             v
           agent --(no tool calls)--> END
             ^ |
             | v
           tools
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from app.agent.orchestration.edges import route_after_agent, route_after_guardrail
from app.agent.orchestration.nodes import GuardrailNode, LLMNode
from app.agent.orchestration.state import AgentState
from app.agent.prompts import SYSTEM_PROMPT
from app.domain.ports.guardrail import Guardrail


class AgentGraphBuilder:
    def __init__(self, llm: BaseChatModel, tools: list[BaseTool], guardrail: Guardrail) -> None:
        self._llm = llm
        self._tools = tools
        self._guardrail = guardrail
        self._system_prompt = SYSTEM_PROMPT
        self._max_history = 20
        self._checkpointer: BaseCheckpointSaver | None = None

    def with_system_prompt(self, prompt: str) -> AgentGraphBuilder:
        self._system_prompt = prompt
        return self

    def with_history_window(self, max_messages: int) -> AgentGraphBuilder:
        self._max_history = max_messages
        return self

    def with_checkpointer(self, checkpointer: BaseCheckpointSaver | None) -> AgentGraphBuilder:
        self._checkpointer = checkpointer
        return self

    def build(self) -> CompiledStateGraph:
        graph = StateGraph(AgentState)
        graph.add_node("guardrail", GuardrailNode(self._guardrail))
        graph.add_node(
            "agent",
            LLMNode(
                self._llm,
                self._tools,
                system_prompt=self._system_prompt,
                max_history_messages=self._max_history,
            ),
        )
        graph.add_node("tools", ToolNode(self._tools))

        graph.add_edge(START, "guardrail")
        graph.add_conditional_edges("guardrail", route_after_guardrail, {"agent": "agent", END: END})
        graph.add_conditional_edges("agent", route_after_agent, {"tools": "tools", END: END})
        graph.add_edge("tools", "agent")

        return graph.compile(checkpointer=self._checkpointer)
