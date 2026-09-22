"""Conversation memory backend for the graph (LangGraph checkpointer).

In-memory today; swapping to Postgres/Redis (``langgraph-checkpoint-postgres``)
is a one-line change here and nowhere else.
"""

from __future__ import annotations

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver


def create_checkpointer() -> BaseCheckpointSaver:
    return InMemorySaver()
