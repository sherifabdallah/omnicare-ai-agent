"""Map the messages produced in one graph turn to a domain AssistantReply (Mapper)."""

from __future__ import annotations

from collections.abc import Sequence

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

from app.agent.prompts import EMPTY_ANSWER_FALLBACK
from app.agent.tools.search_policy import TOOL_NAME as SEARCH_POLICY
from app.domain.models.conversation import AssistantReply, Citation, ToolInvocation


def messages_from(messages: Sequence[BaseMessage], message_id: str) -> list[BaseMessage]:
    """The message with the given id and everything after it (empty if not found)."""
    for index, msg in enumerate(messages):
        if msg.id == message_id:
            return list(messages[index:])
    return []


def messages_after(messages: Sequence[BaseMessage], message_id: str) -> list[BaseMessage]:
    """Messages produced during a turn, i.e. after the user's message."""
    for index, msg in enumerate(messages):
        if msg.id == message_id:
            return list(messages[index + 1 :])
    return list(messages)


def build_reply(turn: Sequence[BaseMessage]) -> AssistantReply:
    tool_results = {m.tool_call_id: m for m in turn if isinstance(m, ToolMessage)}

    invocations: list[ToolInvocation] = []
    citations: list[Citation] = []
    answer = ""

    for msg in turn:
        if not isinstance(msg, AIMessage):
            continue
        for call in msg.tool_calls:
            result_msg = tool_results.get(call["id"])
            result, status = None, "pending"
            if result_msg is not None:
                result = result_msg.artifact if result_msg.artifact is not None else result_msg.content
                status = result_msg.status
                if call["name"] == SEARCH_POLICY and isinstance(result_msg.artifact, list):
                    citations.extend(Citation.model_validate(item) for item in result_msg.artifact)
            invocations.append(ToolInvocation(name=call["name"], args=dict(call["args"]), result=result, status=status))
        if msg.text:
            answer = msg.text

    # Unique citations, in retrieval order.
    seen: set[str] = set()
    unique = [c for c in citations if not (c.section in seen or seen.add(c.section))]

    return AssistantReply(
        text=answer.strip() or EMPTY_ANSWER_FALLBACK,
        citations=unique,
        tool_invocations=invocations,
    )
