"""Claim entities and value objects."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

CLAIM_ID_PATTERN = re.compile(r"^CLM-\d{4}$")
POLICY_NUMBER_PATTERN = re.compile(r"^POL-\d{4}$")

ClaimType = Literal["Water Damage", "Personal Property"]
ClaimStatus = Literal["Submitted", "Under Review", "Approved", "Rejected"]


class Claim(BaseModel):
    """A claim record (entity, identified by claim_id)."""

    model_config = ConfigDict(extra="ignore")

    claim_id: str = Field(pattern=CLAIM_ID_PATTERN.pattern)
    policy_number: str = Field(pattern=POLICY_NUMBER_PATTERN.pattern)
    claim_type: ClaimType
    status: ClaimStatus
    amount: float = Field(gt=0)
    description: str | None = None


class ClaimSubmission(BaseModel):
    """Value object: validated input for submitting a new claim.

    Doubles as the agent tool's argument schema, so anything the LLM passes is
    validated *before* it can reach the application or data layers.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    policy_number: str = Field(
        description="Policy number in the format POL-#### (e.g. POL-1092).",
        pattern=POLICY_NUMBER_PATTERN.pattern,
    )
    claim_type: ClaimType = Field(description='Type of claim: "Water Damage" or "Personal Property".')
    amount: float = Field(description="Claimed amount in USD. Must be greater than 0.", gt=0, le=1_000_000)
    description: str = Field(
        description="Short description of what happened (10-500 characters).",
        min_length=10,
        max_length=500,
    )

    @field_validator("policy_number", mode="before")
    @classmethod
    def _upper(cls, value: object) -> object:
        return value.upper() if isinstance(value, str) else value

    @field_validator("claim_type", mode="before")
    @classmethod
    def _normalise_claim_type(cls, value: object) -> object:
        """Accept case/spacing variations the LLM might produce ("water damage")."""
        if not isinstance(value, str):
            return value
        canonical = {"water damage": "Water Damage", "personal property": "Personal Property"}
        return canonical.get(" ".join(value.lower().split()), value)


def normalise_claim_id(raw: str) -> str:
    return raw.strip().upper()


def is_valid_claim_id(claim_id: str) -> bool:
    return bool(CLAIM_ID_PATTERN.match(claim_id))
