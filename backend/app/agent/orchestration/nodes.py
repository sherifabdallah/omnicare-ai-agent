"""Graph nodes. Each is a small callable class so its collaborators are injected
explicitly (testable) instead of captured from module globals.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import RemoveMessage, SystemMessage, trim_messages
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool

from app.agent.orchestration.state import AgentState
from app.domain.ports.guardrail import Guardrail


class GuardrailNode:
    """Screens the newest user message. Blocked messages are *removed* from the
    thread so they never become part of the memory later LLM calls see."""

    def __init__(self, guardrail: Guardrail) -> None:
        self._guardrail = guardrail

    def __call__(self, state: AgentState) -> dict:
        latest = state["messages"][-1]
        verdict = self._guardrail.check(str(latest.content))
        if verdict.blocked:
            return {
                "messages": [RemoveMessage(id=latest.id)],
                "guardrail": {"blocked": True, "reason": verdict.reason},
            }
        return {"guardrail": {"blocked": False, "reason": None}}


class LLMNode:
    """Calls the tool-enabled chat model with the system prompt and a bounded
    window of history."""

    def __init__(
        self,
        llm: BaseChatModel,
        tools: list[BaseTool],
        *,
        system_prompt: str,
        max_history_messages: int = 20,
    ) -> None:
        self._model: Runnable = llm.bind_tools(tools)
        self._system_message = SystemMessage(content=system_prompt)
        self._max_history = max_history_messages

    async def __call__(self, state: AgentState) -> dict:
        # Never start the window on a tool message: providers reject orphaned tool results.
        history = trim_messages(
            state["messages"],
            max_tokens=self._max_history,
            token_counter=len,
            strategy="last",
            start_on="human",
            include_system=False,
        )
        response = await self._model.ainvoke([self._system_message, *history])
        return {"messages": [response]}
