"""Policy document value objects used by retrieval."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyChunk:
    """A citable passage of the policy document."""

    id: str
    text: str
    source: str  # file name, e.g. "sample_policy.md"
    document: str  # top-level title, e.g. "OmniCare General Insurance Policy 2026"
    section: str  # heading text, e.g. "Section 1: Home Water Damage Coverage"
    chunk_index: int

    @property
    def citation(self) -> str:
        return f"{self.source} — {self.section}"


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: PolicyChunk
    score: float  # similarity in [0, 1]; higher is better

    @property
    def citation(self) -> str:
        return self.chunk.citation
