"""Deterministic guardrail against prompt-injection / jailbreak attempts.

Deliberately *not* an LLM call: it is cheap, predictable, unit-testable and
cannot itself be jailbroken. It is one link in the GuardrailPipeline and is
complemented by the hardened system prompt, strict Pydantic tool schemas and
treating retrieved documents / tool outputs as untrusted data.
"""

from __future__ import annotations

import re
import unicodedata

from app.domain.models.conversation import GuardrailVerdict

# Each entry: (human-readable label, compiled pattern). Patterns run against a
# lower-cased, NFKC-normalised, whitespace-collapsed copy of the message.
_RULES: list[tuple[str, re.Pattern[str]]] = [
    (
        "instruction override",
        re.compile(
            r"\b(ignore|disregard|forget|override|bypass|skip)\b.{0,40}\b"
            r"(previous|prior|above|earlier|all|any|your|the|these|system)\b.{0,20}\b"
            r"(instructions?|prompts?|rules?|guidelines?|policies|policy|directives?"
            r"|constraints?|guardrails?|restrictions?)\b"
        ),
    ),
    (
        "system prompt extraction",
        re.compile(
            r"\b(reveal|show|print|display|repeat|output|leak|dump|tell me|what (is|are))\b.{0,40}\b"
            r"(system prompt|system message|developer message|hidden prompt|initial prompt"
            r"|your (instructions|prompt|rules|guidelines))\b"
        ),
    ),
    (
        "role hijack",
        re.compile(
            r"\b(you are now|from now on you are|act as (an? )?(unrestricted|unfiltered|evil)"
            r"|pretend (you are|to be)|roleplay as)\b"
        ),
    ),
    (
        "jailbreak keyword",
        re.compile(r"\b(jailbreak|jailbroken|dan mode|developer mode|do anything now|god mode|no restrictions mode)\b"),
    ),
    (
        "new instruction injection",
        re.compile(r"(^|\n|[.!?]\s*)(new|updated|real|actual|secret) (instructions?|system prompt|rules?)\s*[:\-]"),
    ),
    (
        "chat template injection",
        re.compile(
            r"(<\|?\s*/?\s*(system|im_start|im_end|assistant|user)\s*\|?>"
            r"|\[/?inst\]|<<\s*sys\s*>>|###\s*(system|instruction))"
        ),
    ),
    (
        "tool / data tampering",
        re.compile(r"\b(mark|set|change|update|force)\b.{0,30}\b(claim|status)\b.{0,30}\b(approved|paid|rejected)\b"),
    ),
]


def normalise(text: str) -> str:
    """Fold unicode look-alikes and whitespace tricks before matching."""
    text = unicodedata.normalize("NFKC", text)
    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in "\n\t")
    return re.sub(r"[ \t]+", " ", text).strip().lower()


class PromptInjectionGuardrail:
    """Implements the Guardrail port with a rule set."""

    name = "prompt_injection"

    def __init__(self, rules: list[tuple[str, re.Pattern[str]]] | None = None) -> None:
        self._rules = rules if rules is not None else _RULES

    def check(self, message: str) -> GuardrailVerdict:
        normalised = normalise(message)
        for label, pattern in self._rules:
            if pattern.search(normalised):
                return GuardrailVerdict.block(label)
        return GuardrailVerdict.allow()
