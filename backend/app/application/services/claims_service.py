"""Use cases around claims. Depends only on the ClaimsRepository port."""

from __future__ import annotations

import logging

from app.domain.exceptions import ClaimNotFoundError, InvalidClaimIdError
from app.domain.models.claim import Claim, ClaimSubmission, is_valid_claim_id, normalise_claim_id
from app.domain.ports.claims_repository import ClaimsRepository

logger = logging.getLogger(__name__)


class ClaimsService:
    def __init__(self, repository: ClaimsRepository) -> None:
        self._repository = repository

    def get_status(self, claim_id: str) -> Claim:
        claim_id = normalise_claim_id(claim_id)
        if not is_valid_claim_id(claim_id):
            raise InvalidClaimIdError(claim_id)
        claim = self._repository.find_by_id(claim_id)
        if claim is None:
            raise ClaimNotFoundError(claim_id)
        return claim

    def submit(self, submission: ClaimSubmission) -> Claim:
        claim = self._repository.add(submission)
        logger.info("Submitted claim %s for policy %s", claim.claim_id, claim.policy_number)
        return claim
