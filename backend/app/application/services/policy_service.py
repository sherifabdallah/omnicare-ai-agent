"""Use case: find the policy passages relevant to a question."""

from __future__ import annotations

from app.domain.models.policy import RetrievedChunk
from app.domain.ports.policy_retriever import PolicyRetriever


class PolicyService:
    def __init__(self, retriever: PolicyRetriever, *, top_k: int = 3) -> None:
        self._retriever = retriever
        self._top_k = top_k

    def search(self, query: str) -> list[RetrievedChunk]:
        return self._retriever.search(query, k=self._top_k)
