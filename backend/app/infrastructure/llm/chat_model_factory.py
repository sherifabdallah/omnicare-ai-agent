"""Chat-model factory (Factory + Registry).

Each provider is a small builder registered by name, so adding a provider is
an *addition* (a new builder) rather than a modification of a growing if/else
chain (Open/Closed Principle). All providers here have a free tier or run locally.
"""

from __future__ import annotations

from collections.abc import Callable

from langchain_core.language_models import BaseChatModel

from app.core.config import Settings
from app.core.exceptions import ConfigurationError

ProviderBuilder = Callable[[Settings], BaseChatModel]


class ChatModelFactory:
    _builders: dict[str, ProviderBuilder] = {}

    @classmethod
    def register(cls, provider: str) -> Callable[[ProviderBuilder], ProviderBuilder]:
        def decorator(builder: ProviderBuilder) -> ProviderBuilder:
            cls._builders[provider] = builder
            return builder

        return decorator

    @classmethod
    def providers(cls) -> list[str]:
        return sorted(cls._builders)

    @classmethod
    def create(cls, settings: Settings) -> BaseChatModel:
        try:
            builder = cls._builders[settings.llm_provider]
        except KeyError as exc:
            raise ConfigurationError(
                f"Unsupported LLM_PROVIDER {settings.llm_provider!r}; choose one of {cls.providers()}"
            ) from exc
        return builder(settings)


def _require(value: str | None, env_name: str) -> str:
    if not value:
        raise ConfigurationError(
            f"{env_name} is not set. Add it to your .env (see .env.example) or choose another LLM_PROVIDER."
        )
    return value


@ChatModelFactory.register("groq")
def _groq(settings: Settings) -> BaseChatModel:
    from langchain_groq import ChatGroq

    return ChatGroq(
        model=settings.resolved_model,
        api_key=_require(settings.groq_api_key, "GROQ_API_KEY"),
        temperature=settings.llm_temperature,
        timeout=settings.llm_timeout_seconds,
    )


@ChatModelFactory.register("openai")
def _openai(settings: Settings) -> BaseChatModel:
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=settings.resolved_model,
        api_key=_require(settings.openai_api_key, "OPENAI_API_KEY"),
        temperature=settings.llm_temperature,
        timeout=settings.llm_timeout_seconds,
    )


@ChatModelFactory.register("anthropic")
def _anthropic(settings: Settings) -> BaseChatModel:
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(
        model=settings.resolved_model,
        api_key=_require(settings.anthropic_api_key, "ANTHROPIC_API_KEY"),
        temperature=settings.llm_temperature,
        timeout=settings.llm_timeout_seconds,
    )


@ChatModelFactory.register("ollama")
def _ollama(settings: Settings) -> BaseChatModel:
    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=settings.resolved_model,
        base_url=settings.ollama_base_url,
        temperature=settings.llm_temperature,
    )
