"""Use case: find the policy passages relevant to a question.

Retrieval returns the nearest chunks by similarity, but "nearest" is not the
same as "relevant": with a small corpus the store will happily return every
chunk it has, including ones that have nothing to do with the question. Citing
those would make the sources list meaningless, so this service decides what
actually counts as relevant.
"""

from __future__ import annotations

import logging

from app.domain.models.policy import RetrievedChunk
from app.domain.ports.policy_retriever import PolicyRetriever

logger = logging.getLogger(__name__)


class PolicyService:
    def __init__(
        self,
        retriever: PolicyRetriever,
        *,
        top_k: int = 3,
        min_score: float = 0.15,
        relative_cutoff: float = 0.5,
    ) -> None:
        self._retriever = retriever
        self._top_k = top_k
        self._min_score = min_score
        self._relative_cutoff = relative_cutoff

    def search(self, query: str) -> list[RetrievedChunk]:
        hits = self._retriever.search(query, k=self._top_k)
        if not hits:
            return []

        # Always keep the best match so the agent has something to reason over,
        # even for a vague question. Judge the rest against it.
        best = hits[0]
        floor = max(self._min_score, best.score * self._relative_cutoff)
        relevant = [best, *(h for h in hits[1:] if h.score >= floor)]

        if len(relevant) < len(hits):
            logger.debug(
                "Dropped %d weak passage(s) below %.3f for query %r",
                len(hits) - len(relevant),
                floor,
                query,
            )
        return relevant
