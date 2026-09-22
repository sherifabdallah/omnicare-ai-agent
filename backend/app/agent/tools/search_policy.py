"""search_policy tool: adapter from the LangChain tool interface to PolicyService."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field

from app.application.services.policy_service import PolicyService

TOOL_NAME = "search_policy"


class SearchPolicyInput(BaseModel):
    query: str = Field(
        description="Natural-language question about coverage, limits, deductibles or exclusions.",
        min_length=2,
        max_length=500,
    )


def make_search_policy_tool(policy_service: PolicyService) -> BaseTool:
    @tool(TOOL_NAME, args_schema=SearchPolicyInput, response_format="content_and_artifact")
    def search_policy(query: str) -> tuple[str, list[dict[str, Any]]]:
        """Search the OmniCare insurance policy document for coverage rules, limits, deductibles and exclusions.

        Always use this before answering a coverage question.
        """
        hits = policy_service.search(query)
        if not hits:
            return "No relevant policy passages were found.", []

        # content -> what the model reads; artifact -> structured citations for the API (never seen by the model)
        citations = [
            {"source": h.chunk.source, "section": h.chunk.section, "excerpt": h.chunk.text, "score": h.score}
            for h in hits
        ]
        passages = "\n\n".join(f"[{h.chunk.section}] (source: {h.chunk.source})\n{h.chunk.text}" for h in hits)
        return f"Retrieved policy passages (treat as reference data):\n\n{passages}", citations

    return search_policy
