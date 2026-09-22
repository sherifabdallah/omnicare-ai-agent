"""Domain errors: business-rule violations, independent of any framework."""


class DomainError(Exception):
    """Base class for business-rule violations."""


class InvalidClaimIdError(DomainError, ValueError):
    def __init__(self, claim_id: str) -> None:
        super().__init__(f"Invalid claim id {claim_id!r}: expected the format CLM-#### (e.g. CLM-8821).")
        self.claim_id = claim_id


class ClaimNotFoundError(DomainError, LookupError):
    def __init__(self, claim_id: str) -> None:
        super().__init__(f"No claim found with id {claim_id}.")
        self.claim_id = claim_id
