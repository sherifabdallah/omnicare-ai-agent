"""Application-level (non-domain) exceptions."""


class AppError(Exception):
    """Base class for errors raised by the application or its adapters."""


class ConfigurationError(AppError):
    """The service is mis-configured (e.g. missing API key)."""


class AssistantUnavailableError(AppError):
    """The agent runtime or LLM provider failed while answering."""
