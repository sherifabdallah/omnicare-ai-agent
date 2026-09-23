"""Shared fixtures.

The agent is exercised end-to-end through the real LangGraph workflow, real
tools, real vector store and a *scripted* chat model, so the suite runs
offline and needs no API key. Live-provider tests live in tests/live.
"""

from __future__ import annotations

import json
import os
import shutil
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import Field

# Make app import/start-up work without real credentials. Skipped for live runs,
# where the real provider settings must come from the environment or .env -
# an env var set here would take precedence over .env and break authentication.
if os.environ.get("RUN_LIVE_TESTS") != "1":
    os.environ.setdefault("LLM_PROVIDER", "groq")
    os.environ.setdefault("GROQ_API_KEY", "test-key")

# Tests keep the vector index in memory so a run never writes into ./data.
os.environ.setdefault("PERSIST_VECTOR_STORE", "false")

from app.agent.guardrails import GuardrailPipeline, PromptInjectionGuardrail  # noqa: E402
from app.agent.orchestration.graph_builder import AgentGraphBuilder  # noqa: E402
from app.agent.runtime.langgraph_assistant import LangGraphAssistant  # noqa: E402
from app.agent.tools import build_tools  # noqa: E402
from app.api.dependencies import get_conversation_service  # noqa: E402
from app.application.services import ClaimsService, ConversationService, PolicyService  # noqa: E402
from app.infrastructure.persistence.json_claims_repository import JsonClaimsRepository  # noqa: E402
from app.infrastructure.vector_store.chroma_policy_retriever import ChromaPolicyRetriever  # noqa: E402
from app.main import app  # noqa: E402

REPO_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class ScriptedChatModel(BaseChatModel):
    """Returns pre-canned AIMessages in order; records every prompt it receives."""

    responses: list[AIMessage]
    calls: list[list[BaseMessage]] = Field(default_factory=list)

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        self.calls.append(list(messages))
        index = min(len(self.calls) - 1, len(self.responses) - 1)
        return ChatResult(generations=[ChatGeneration(message=self.responses[index])])

    def bind_tools(self, tools: Any, **kwargs: Any) -> ScriptedChatModel:
        return self

    @property
    def _llm_type(self) -> str:
        return "scripted"


def tool_call(name: str, args: dict[str, Any], call_id: str = "call_1") -> AIMessage:
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id, "type": "tool_call"}])


# --- data ---------------------------------------------------------------------


# The claims the suite asserts against. Owned by the tests rather than copied from
# ./data, because that file is a live store the running app appends to.
SEED_CLAIMS = [
    {
        "claim_id": "CLM-8821",
        "policy_number": "POL-1092",
        "claim_type": "Water Damage",
        "status": "Approved",
        "amount": 3500.0,
    },
    {
        "claim_id": "CLM-9014",
        "policy_number": "POL-3341",
        "claim_type": "Personal Property",
        "status": "Under Review",
        "amount": 1200.0,
    },
]


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """A throw-away data directory so tests never touch the real files."""
    shutil.copy(REPO_DATA_DIR / "sample_policy.md", tmp_path / "sample_policy.md")
    (tmp_path / "mock_claims.json").write_text(json.dumps(SEED_CLAIMS, indent=2), encoding="utf-8")
    return tmp_path


@pytest.fixture(scope="session")
def retriever() -> ChromaPolicyRetriever:
    return ChromaPolicyRetriever.from_markdown(REPO_DATA_DIR / "sample_policy.md")


@pytest.fixture
def claims_repo(data_dir: Path) -> JsonClaimsRepository:
    return JsonClaimsRepository(data_dir / "mock_claims.json")


@pytest.fixture
def claims_service(claims_repo: JsonClaimsRepository) -> ClaimsService:
    return ClaimsService(claims_repo)


@pytest.fixture
def policy_service(retriever: ChromaPolicyRetriever) -> PolicyService:
    return PolicyService(retriever, top_k=2)


@pytest.fixture
def tools(policy_service: PolicyService, claims_service: ClaimsService):
    return build_tools(policy_service, claims_service)


# --- agent -------------------------------------------------------------------


@pytest.fixture
def make_assistant(tools):
    """Factory: build a LangGraphAssistant around a scripted LLM with the given responses."""

    def _make(responses: list[AIMessage]) -> tuple[LangGraphAssistant, ScriptedChatModel]:
        llm = ScriptedChatModel(responses=responses)
        graph = (
            AgentGraphBuilder(llm, tools, guardrail=GuardrailPipeline([PromptInjectionGuardrail()]))
            .with_checkpointer(InMemorySaver())
            .build()
        )
        return LangGraphAssistant(graph), llm

    return _make


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def override_service(client: TestClient):
    """Replace the ConversationService used by the API for one test."""

    def _override(service: ConversationService) -> None:
        app.dependency_overrides[get_conversation_service] = lambda: service

    return _override
