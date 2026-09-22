"""Turn a markdown policy document into citable chunks.

1. Split on markdown headings so every chunk knows which *section* it came
   from (that is what we cite).
2. Sub-split long sections with a recursive character splitter so a single
   chunk never exceeds the useful context of the embedding model.
"""

from __future__ import annotations

from pathlib import Path

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from app.domain.models.policy import PolicyChunk

HEADERS_TO_SPLIT_ON = [("#", "document"), ("##", "section")]


def chunk_markdown_policy(path: Path, *, chunk_size: int = 800, chunk_overlap: int = 100) -> list[PolicyChunk]:
    if not path.exists():
        raise FileNotFoundError(f"Policy document not found: {path}")

    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS_TO_SPLIT_ON, strip_headers=True)
    size_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    sections = header_splitter.split_text(path.read_text(encoding="utf-8"))
    documents = size_splitter.split_documents(sections)

    chunks: list[PolicyChunk] = []
    for index, doc in enumerate(documents):
        text = doc.page_content.strip()
        if not text:
            continue
        chunks.append(
            PolicyChunk(
                id=f"{path.stem}-{index}",
                text=text,
                source=path.name,
                document=doc.metadata.get("document", path.stem),
                section=doc.metadata.get("section", "Untitled section"),
                chunk_index=index,
            )
        )
    if not chunks:
        raise ValueError(f"No content could be extracted from {path}")
    return chunks
