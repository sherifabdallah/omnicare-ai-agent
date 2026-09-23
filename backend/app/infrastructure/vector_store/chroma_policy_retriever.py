"""PolicyRetriever adapter: a local Chroma vector store with on-CPU embeddings.

Pipeline
--------
1. `markdown_chunker` splits the policy into section-aware chunks, each keeping
   the heading it came from - that heading is what we cite.
2. Every chunk is embedded with Chroma's bundled all-MiniLM-L6-v2 ONNX model,
   which runs locally on CPU (no API calls, no cost).
3. Vectors live in a persistent Chroma collection on disk (`DATA_DIR/.chroma`
   by default), so the index survives restarts instead of being rebuilt.
4. `search` embeds the query and returns the nearest chunks by cosine
   similarity, with their section metadata for citations.

Chunk ids are deterministic, so start-up upserts are idempotent: unchanged
chunks are refreshed in place, edited ones are overwritten, and chunks removed
from the document are deleted from the collection.
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
    def __init__(self, chunks: list[PolicyChunk], *, persist_dir: Path | None = None) -> None:
        if persist_dir is not None:
            persist_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(persist_dir))
        else:
            # Used by tests, where a throw-away index is faster than touching disk.
            self._client = chromadb.EphemeralClient()

        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=DefaultEmbeddingFunction(),
            metadata={"hnsw:space": "cosine"},
        )
        self._chunks_by_id = {chunk.id: chunk for chunk in chunks}
        self._sync(chunks)
        logger.info(
            "Vector store ready: %d chunks in '%s' (%s)",
            self._collection.count(),
            COLLECTION_NAME,
            persist_dir or "in-memory",
        )

    @classmethod
    def from_markdown(
        cls,
        path: Path,
        *,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        persist_dir: Path | None = None,
    ) -> ChromaPolicyRetriever:
        chunks = chunk_markdown_policy(path, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return cls(chunks, persist_dir=persist_dir)

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

    # --- internals -----------------------------------------------------------------

    def _sync(self, chunks: list[PolicyChunk]) -> None:
        """Make the collection match the document exactly (idempotent)."""
        self._collection.upsert(
            ids=[c.id for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[
                {"source": c.source, "section": c.section, "document": c.document, "chunk_index": c.chunk_index}
                for c in chunks
            ],
        )
        stale = set(self._collection.get(include=[])["ids"]) - {c.id for c in chunks}
        if stale:
            logger.info("Removing %d chunk(s) no longer in the document", len(stale))
            self._collection.delete(ids=sorted(stale))
