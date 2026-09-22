"""PolicyRetriever adapter: Chroma (in-process) + local ONNX MiniLM embeddings.

Zero external cost: the embedding model runs on CPU. The collection is
in-memory and rebuilt at start-up because the corpus is tiny and re-ingesting
is cheaper than reasoning about staleness.
"""

from __future__ import annotations

import logging
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from app.domain.models.policy import PolicyChunk, RetrievedChunk
from app.infrastructure.vector_store.markdown_chunker import chunk_markdown_policy

logger = logging.getLogger(__name__)

COLLECTION_NAME = "omnicare_policy"


class ChromaPolicyRetriever:
    def __init__(self, chunks: list[PolicyChunk]) -> None:
        self._client = chromadb.EphemeralClient()
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=DefaultEmbeddingFunction(),
            metadata={"hnsw:space": "cosine"},
        )
        self._chunks_by_id = {chunk.id: chunk for chunk in chunks}
        self._collection.add(
            ids=[c.id for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[
                {"source": c.source, "section": c.section, "document": c.document, "chunk_index": c.chunk_index}
                for c in chunks
            ],
        )
        logger.info("Indexed %d policy chunks into '%s'", len(chunks), COLLECTION_NAME)

    @classmethod
    def from_markdown(cls, path: Path, *, chunk_size: int = 800, chunk_overlap: int = 100) -> ChromaPolicyRetriever:
        return cls(chunk_markdown_policy(path, chunk_size=chunk_size, chunk_overlap=chunk_overlap))

    # --- PolicyRetriever port ---------------------------------------------------

    def __len__(self) -> int:
        return len(self._chunks_by_id)

    def search(self, query: str, *, k: int = 3) -> list[RetrievedChunk]:
        query = query.strip()
        if not query:
            return []
        result = self._collection.query(
            query_texts=[query],
            n_results=min(k, len(self._chunks_by_id)),
            include=["distances"],
        )
        hits: list[RetrievedChunk] = []
        for chunk_id, distance in zip(result["ids"][0], result["distances"][0], strict=True):
            # Chroma returns cosine *distance* (0 = identical); convert to similarity.
            score = max(0.0, min(1.0, 1.0 - float(distance)))
            hits.append(RetrievedChunk(chunk=self._chunks_by_id[chunk_id], score=round(score, 4)))
        return hits
