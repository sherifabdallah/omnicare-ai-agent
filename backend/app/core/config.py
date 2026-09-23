"""Application settings, loaded from environment variables / .env.

`core` is the only layer every other layer may import from; it holds
cross-cutting concerns (configuration, logging, base exceptions) and nothing
about the business domain.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repository root (…/omnicare-ai-agent). Used only to locate the default data dir
# when running outside Docker; inside the container DATA_DIR is set explicitly.
_REPO_ROOT = Path(__file__).resolve().parents[3]

LLMProvider = Literal["groq", "openai", "anthropic", "ollama"]

DEFAULT_MODELS: dict[str, str] = {
    "groq": "openai/gpt-oss-120b",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-sonnet-5",
    "ollama": "llama3.1",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(_REPO_ROOT / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- LLM -------------------------------------------------------------
    llm_provider: LLMProvider = "groq"
    llm_model: str | None = Field(default=None, description="Overrides the provider default model.")
    llm_temperature: float = 0.0
    llm_timeout_seconds: float = 60.0

    groq_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"

    # --- Data / RAG --------------------------------------------------------
    data_dir: Path = _REPO_ROOT / "data"
    policy_doc_name: str = "sample_policy.md"
    claims_db_name: str = "mock_claims.json"
    rag_top_k: int = 3
    rag_chunk_size: int = 800
    rag_chunk_overlap: int = 100
    vector_store_dir: Path | None = Field(
        default=None, description="Where the Chroma index lives. Defaults to DATA_DIR/.chroma."
    )
    persist_vector_store: bool = Field(
        default=True, description="Set false to keep the index in memory (used by tests)."
    )

    # --- Agent -------------------------------------------------------------
    max_history_messages: int = 20
    max_agent_steps: int = 8

    # --- API ---------------------------------------------------------------
    cors_origins: list[str] = ["*"]
    log_level: str = "INFO"

    @property
    def resolved_model(self) -> str:
        return self.llm_model or DEFAULT_MODELS[self.llm_provider]

    @property
    def policy_doc_path(self) -> Path:
        return self.data_dir / self.policy_doc_name

    @property
    def claims_db_path(self) -> Path:
        return self.data_dir / self.claims_db_name

    @property
    def vector_store_path(self) -> Path | None:
        """Directory for the on-disk vector index, or None to keep it in memory."""
        if not self.persist_vector_store:
            return None
        return self.vector_store_dir or (self.data_dir / ".chroma")


@lru_cache
def get_settings() -> Settings:
    return Settings()
