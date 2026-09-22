"""LangGraphAssistant: the Assistant port implemented on top of the compiled graph (Adapter).

Owns everything LangGraph-specific about *running* a turn: thread config,
per-user serialisation, step limits, and rolling back half-finished turns so
memory never ends up with dangling tool calls.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from uuid import uuid4

from langchain_core.messages import HumanMessage, RemoveMessage
from langgraph.errors import GraphRecursionError
from langgraph.graph.state import CompiledStateGraph

from app.agent.prompts import INJECTION_REFUSAL, STEP_LIMIT_RESPONSE
from app.agent.runtime.reply_builder import build_reply, messages_after, messages_from
from app.core.exceptions import AssistantUnavailableError
from app.domain.models.conversation import AssistantReply

logger = logging.getLogger(__name__)


class LangGraphAssistant:
    def __init__(self, graph: CompiledStateGraph, *, max_agent_steps: int = 8) -> None:
        self._graph = graph
        # Each graph "step" is one node: agent+tools alternate, plus the guardrail.
        self._recursion_limit = 2 * max_agent_steps + 2
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    # --- Assistant port ----------------------------------------------------------

    async def chat(self, user_id: str, message: str) -> AssistantReply:
        human = HumanMessage(content=message, id=str(uuid4()))
        config = {"configurable": {"thread_id": user_id}, "recursion_limit": self._recursion_limit}

        # Serialise turns per user so concurrent requests cannot interleave one thread.
        async with self._locks[user_id]:
            try:
                state = await self._graph.ainvoke({"messages": [human]}, config=config)
            except GraphRecursionError:
                logger.warning("Agent hit the step limit for user %s", user_id)
                await self._rollback_turn(config, human.id)
                return AssistantReply(text=STEP_LIMIT_RESPONSE)
            except Exception as exc:
                await self._rollback_turn(config, human.id)
                raise AssistantUnavailableError(str(exc)) from exc

        if state["guardrail"]["blocked"]:
            return AssistantReply(text=INJECTION_REFUSAL, blocked=True)

        return build_reply(messages_after(state["messages"], human.id))

    async def reset(self, user_id: str) -> None:
        if self._graph.checkpointer is not None:
            await self._graph.checkpointer.adelete_thread(user_id)

    # --- internals -----------------------------------------------------------------

    async def _rollback_turn(self, config: dict, human_id: str) -> None:
        """Drop a half-finished turn so a provider error or step limit cannot corrupt memory."""
        if self._graph.checkpointer is None:
            return
        try:
            snapshot = await self._graph.aget_state(config)
            stale = messages_from(snapshot.values.get("messages", []), human_id)
            if stale:
                await self._graph.aupdate_state(config, {"messages": [RemoveMessage(id=m.id) for m in stale]})
        except Exception:  # best effort: never mask the original error
            logger.exception("Could not roll back turn for thread %s", config["configurable"]["thread_id"])
