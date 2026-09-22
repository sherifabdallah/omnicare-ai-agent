"""Live tests against the configured LLM provider.

Skipped unless RUN_LIVE_TESTS=1 (and the provider key is configured), so the
default suite stays free and offline:

    RUN_LIVE_TESTS=1 pytest -m live -v
"""

import json
import os
from pathlib import Path

import pytest

from app.bootstrap import build_container
from app.core.config import Settings
from app.core.exceptions import ConfigurationError
from app.infrastructure.llm.chat_model_factory import ChatModelFactory

pytestmark = pytest.mark.live

if os.environ.get("RUN_LIVE_TESTS") != "1":
    pytest.skip("set RUN_LIVE_TESTS=1 to run live LLM tests", allow_module_level=True)


@pytest.fixture
def live_service(data_dir: Path):
    settings = Settings(data_dir=data_dir)
    try:
        ChatModelFactory.create(settings)
    except ConfigurationError as exc:
        pytest.skip(str(exc))
    return build_container(settings).conversation_service


async def test_live_coverage_question_cites_policy(live_service) -> None:
    reply = await live_service.chat("live_1", "Is water damage from a burst pipe covered? What is the deductible?")

    assert any(t.name == "search_policy" for t in reply.tool_invocations)
    assert any("Section 1" in s for s in reply.sources)
    assert "25,000" in reply.text and "500" in reply.text


async def test_live_claim_status(live_service) -> None:
    reply = await live_service.chat("live_2", "What is the status of claim CLM-8821?")

    assert any(t.name == "get_claim_status" for t in reply.tool_invocations)
    assert "approved" in reply.text.lower()


async def test_live_submit_claim(live_service, data_dir: Path) -> None:
    reply = await live_service.chat(
        "live_3",
        "Please submit a water damage claim for policy POL-1092 for $1,800. "
        "A pipe burst under the kitchen sink and damaged the cabinets.",
    )

    submit_calls = [t for t in reply.tool_invocations if t.name == "submit_claim"]
    assert len(submit_calls) == 1
    claim_id = submit_calls[0].result["claim_id"]
    assert claim_id in reply.text
    on_disk = json.loads((data_dir / "mock_claims.json").read_text(encoding="utf-8"))
    assert on_disk[-1]["claim_id"] == claim_id
