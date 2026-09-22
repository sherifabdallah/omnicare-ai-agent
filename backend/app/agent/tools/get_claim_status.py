"""get_claim_status tool: adapter from the LangChain tool interface to ClaimsService."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field

from app.application.services.claims_service import ClaimsService
from app.domain.exceptions import DomainError

TOOL_NAME = "get_claim_status"


class GetClaimStatusInput(BaseModel):
    claim_id: str = Field(
        description="The claim identifier in the format CLM-#### (e.g. CLM-8821).",
        min_length=4,
        max_length=16,
    )


def make_get_claim_status_tool(claims_service: ClaimsService) -> BaseTool:
    @tool(TOOL_NAME, args_schema=GetClaimStatusInput, response_format="content_and_artifact")
    def get_claim_status(claim_id: str) -> tuple[str, dict[str, Any]]:
        """Look up the current status of an existing insurance claim by its claim id."""
        try:
            claim = claims_service.get_status(claim_id)
        except DomainError as exc:
            # Business errors are answers, not crashes: the model relays them to the user.
            return f"Lookup failed: {exc}", {"error": str(exc)}
        record = claim.model_dump(exclude_none=True)
        return f"Claim record found: {json.dumps(record)}", record

    return get_claim_status
