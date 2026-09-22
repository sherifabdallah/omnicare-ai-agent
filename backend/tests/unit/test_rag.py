from pathlib import Path

import pytest

from app.infrastructure.vector_store.chroma_policy_retriever import ChromaPolicyRetriever
from app.infrastructure.vector_store.markdown_chunker import chunk_markdown_policy


def test_chunker_splits_by_section(data_dir: Path) -> None:
    chunks = chunk_markdown_policy(data_dir / "sample_policy.md")

    assert [c.section for c in chunks] == [
        "Section 1: Home Water Damage Coverage",
        "Section 2: Personal Property Protection",
    ]
    assert all(c.source == "sample_policy.md" for c in chunks)
    assert all(c.document == "OmniCare General Insurance Policy 2026" for c in chunks)
    assert "$25,000" in chunks[0].text and "$500 deductible" in chunks[0].text
    assert chunks[1].citation == "sample_policy.md — Section 2: Personal Property Protection"


def test_chunker_sub_splits_long_sections(tmp_path: Path) -> None:
    doc = tmp_path / "long.md"
    doc.write_text("# Doc\n\n## Section 1: Big\n\n" + ("Coverage sentence. " * 200), encoding="utf-8")

    chunks = chunk_markdown_policy(doc, chunk_size=300, chunk_overlap=30)

    assert len(chunks) > 1
    assert {c.section for c in chunks} == {"Section 1: Big"}
    assert all(len(c.text) <= 300 for c in chunks)


def test_chunker_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        chunk_markdown_policy(tmp_path / "nope.md")


def test_retrieval_ranks_water_damage_section_first(retriever: ChromaPolicyRetriever) -> None:
    hits = retriever.search("My pipe burst and flooded the kitchen. Am I covered and what is the deductible?", k=2)

    assert hits[0].chunk.section.startswith("Section 1")
    assert hits[0].score > hits[1].score
    assert 0.0 <= hits[1].score <= hits[0].score <= 1.0


def test_retrieval_ranks_personal_property_section_first(retriever: ChromaPolicyRetriever) -> None:
    hits = retriever.search("Is my jewelry and laptop covered? What about expensive single items?", k=2)

    assert hits[0].chunk.section.startswith("Section 2")
    assert "appraisal" in hits[0].chunk.text


def test_retrieval_respects_k_and_empty_query(retriever: ChromaPolicyRetriever) -> None:
    assert len(retriever.search("water", k=1)) == 1
    assert len(retriever.search("water", k=10)) == len(retriever)  # never more than the corpus
    assert retriever.search("   ") == []
