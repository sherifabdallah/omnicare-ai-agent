"""Composition root: the one place that knows about concrete implementations.

Wires infrastructure adapters -> application services -> agent runtime.
Everything else depends on ports, so this file is the only thing that changes
when an implementation is swapped (JSON -> SQL, Chroma -> Qdrant, Groq -> Ollama).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.agent.guardrails import GuardrailPipeline, PromptInjectionGuardrail
from app.agent.memory.checkpointer import create_checkpointer
from app.agent.orchestration.graph_builder import AgentGraphBuilder
from app.agent.runtime.langgraph_assistant import LangGraphAssistant
from app.agent.tools import build_tools
from app.application.services import ClaimsService, ConversationService, PolicyService
from app.core.config import Settings
from app.domain.ports import Assistant, ClaimsRepository, PolicyRetriever
from app.infrastructure.llm.chat_model_factory import ChatModelFactory
from app.infrastructure.persistence.json_claims_repository import JsonClaimsRepository
from app.infrastructure.vector_store.chroma_policy_retriever import ChromaPolicyRetriever


@dataclass(frozen=True)
class AppContainer:
    settings: Settings
    claims_repository: ClaimsRepository
    policy_retriever: PolicyRetriever
    claims_service: ClaimsService
    policy_service: PolicyService
    assistant: Assistant
    conversation_service: ConversationService


def build_container(settings: Settings) -> AppContainer:
    # Infrastructure
    claims_repository = JsonClaimsRepository(settings.claims_db_path)
    policy_retriever = ChromaPolicyRetriever.from_markdown(
        settings.policy_doc_path,
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
        persist_dir=settings.vector_store_path,
    )
    llm = ChatModelFactory.create(settings)

    # Application
    claims_service = ClaimsService(claims_repository)
    policy_service = PolicyService(policy_retriever, top_k=settings.rag_top_k)

    # Agent
    graph = (
        AgentGraphBuilder(
            llm,
            tools=build_tools(policy_service, claims_service),
            guardrail=GuardrailPipeline([PromptInjectionGuardrail()]),
        )
        .with_history_window(settings.max_history_messages)
        .with_checkpointer(create_checkpointer())
        .build()
    )
    assistant = LangGraphAssistant(graph, max_agent_steps=settings.max_agent_steps)

    return AppContainer(
        settings=settings,
        claims_repository=claims_repository,
        policy_retriever=policy_retriever,
        claims_service=claims_service,
        policy_service=policy_service,
        assistant=assistant,
        conversation_service=ConversationService(assistant),
    )
