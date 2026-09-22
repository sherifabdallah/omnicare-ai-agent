"""The LangChain tool adapters, invoked the way LangGraph's ToolNode invokes them."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError


def invoke(tool, args: dict, call_id: str = "call_1"):
    return tool.invoke({"name": tool.name, "args": args, "id": call_id, "type": "tool_call"})


def by_name(tools, name: str):
    return next(t for t in tools if t.name == name)


def read_claims(data_dir: Path) -> list[dict]:
    return json.loads((data_dir / "mock_claims.json").read_text(encoding="utf-8"))


def test_tool_names(tools) -> None:
    assert [t.name for t in tools] == ["search_policy", "get_claim_status", "submit_claim"]


def test_search_policy_tool_returns_citations(tools) -> None:
    msg = invoke(by_name(tools, "search_policy"), {"query": "burst pipe deductible"})

    assert "Section 1: Home Water Damage Coverage" in msg.content
    assert msg.artifact[0]["section"].startswith("Section 1")
    assert msg.artifact[0]["source"] == "sample_policy.md"
    assert 0 < msg.artifact[0]["score"] <= 1


def test_get_claim_status_tool(tools) -> None:
    get_status = by_name(tools, "get_claim_status")

    found = invoke(get_status, {"claim_id": "CLM-9014"})
    assert found.artifact["status"] == "Under Review"
    assert "Under Review" in found.content

    missing = invoke(get_status, {"claim_id": "CLM-0000"})
    assert missing.artifact == {"error": "No claim found with id CLM-0000."}
    assert "Lookup failed" in missing.content

    malformed = invoke(get_status, {"claim_id": "9014"})
    assert "CLM-####" in malformed.artifact["error"]


def test_submit_claim_tool_persists_and_confirms(tools, data_dir: Path) -> None:
    msg = invoke(
        by_name(tools, "submit_claim"),
        {
            "policy_number": "POL-3341",
            "claim_type": "Personal Property",
            "amount": 800,
            "description": "Laptop stolen from my car overnight.",
        },
    )

    assert "Confirmation id: CLM-" in msg.content
    assert msg.artifact["status"] == "Submitted"
    assert any(c["claim_id"] == msg.artifact["claim_id"] for c in read_claims(data_dir))


def test_submit_claim_tool_rejects_invalid_args(tools, data_dir: Path) -> None:
    with pytest.raises(ValidationError):
        invoke(
            by_name(tools, "submit_claim"),
            {"policy_number": "bad", "claim_type": "Fire", "amount": -1, "description": "x"},
        )

    assert len(read_claims(data_dir)) == 2  # nothing written
