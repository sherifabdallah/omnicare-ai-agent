"""Compose guardrails into one check (Chain of Responsibility).

The first guardrail that blocks wins; adding a new check (e.g. an LLM-based
classifier or a PII filter) means appending to the list, not editing callers.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from app.domain.models.conversation import GuardrailVerdict
from app.domain.ports.guardrail import Guardrail

logger = logging.getLogger(__name__)


class GuardrailPipeline:
    name = "pipeline"

    def __init__(self, guardrails: Sequence[Guardrail]) -> None:
        self._guardrails = list(guardrails)

    def check(self, message: str) -> GuardrailVerdict:
        for guardrail in self._guardrails:
            verdict = guardrail.check(message)
            if verdict.blocked:
                logger.warning("guardrail=%s blocked message (%s)", guardrail.name, verdict.reason)
                return GuardrailVerdict.block(f"{guardrail.name}: {verdict.reason}")
        return GuardrailVerdict.allow()
