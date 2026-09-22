from __future__ import annotations

from typing import Protocol

from app.domain.models.policy import RetrievedChunk


class PolicyRetriever(Protocol):
    """Semantic search over the policy document."""

    def search(self, query: str, *, k: int = 3) -> list[RetrievedChunk]: ...

    def __len__(self) -> int: ...
