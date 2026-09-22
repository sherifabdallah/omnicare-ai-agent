"""Assemble the tool set the agent may call.

Tools are bound to concrete service instances here (no module-level globals),
which keeps every tool trivially testable with fakes.
"""

from __future__ import annotations

from langchain_core.tools import BaseTool

from app.agent.tools.get_claim_status import make_get_claim_status_tool
from app.agent.tools.search_policy import make_search_policy_tool
from app.agent.tools.submit_claim import make_submit_claim_tool
from app.application.services.claims_service import ClaimsService
from app.application.services.policy_service import PolicyService


def build_tools(policy_service: PolicyService, claims_service: ClaimsService) -> list[BaseTool]:
    return [
        make_search_policy_tool(policy_service),
        make_get_claim_status_tool(claims_service),
        make_submit_claim_tool(claims_service),
    ]
