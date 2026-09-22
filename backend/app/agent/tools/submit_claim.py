"""submit_claim tool: adapter from the LangChain tool interface to ClaimsService.

The argument schema *is* the domain value object (ClaimSubmission), so the
LLM cannot pass anything the domain would not accept - invalid arguments are
rejected by the tool runtime and fed back to the model as an error message.
"""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import BaseTool, tool

from app.application.services.claims_service import ClaimsService
from app.domain.models.claim import ClaimSubmission

TOOL_NAME = "submit_claim"


def make_submit_claim_tool(claims_service: ClaimsService) -> BaseTool:
    @tool(TOOL_NAME, args_schema=ClaimSubmission, response_format="content_and_artifact")
    def submit_claim(
        policy_number: str, claim_type: str, amount: float, description: str
    ) -> tuple[str, dict[str, Any]]:
        """Submit a new insurance claim and return the confirmation claim id.

        Requires policy_number (POL-####), claim_type ("Water Damage" or "Personal Property"),
        amount in USD and a short description.
        """
        submission = ClaimSubmission(
            policy_number=policy_number, claim_type=claim_type, amount=amount, description=description
        )
        claim = claims_service.submit(submission)
        record = claim.model_dump(exclude_none=True)
        return f"Claim submitted successfully. Confirmation id: {claim.claim_id}. Record: {json.dumps(record)}", record

    return submit_claim
