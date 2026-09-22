from __future__ import annotations

from typing import Protocol

from app.domain.models.conversation import GuardrailVerdict


class Guardrail(Protocol):
    """A safety check applied to user input before it reaches the model."""

    @property
    def name(self) -> str: ...

    def check(self, message: str) -> GuardrailVerdict: ...
