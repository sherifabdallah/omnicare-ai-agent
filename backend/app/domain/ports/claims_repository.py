from __future__ import annotations

from typing import Protocol

from app.domain.models.claim import Claim, ClaimSubmission


class ClaimsRepository(Protocol):
    """Persistence boundary for claims (Repository pattern)."""

    def list_all(self) -> list[Claim]: ...

    def find_by_id(self, claim_id: str) -> Claim | None: ...

    def add(self, submission: ClaimSubmission) -> Claim:
        """Persist a new claim and return the stored record (with its generated id)."""
        ...
