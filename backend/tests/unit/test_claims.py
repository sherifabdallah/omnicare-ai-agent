"""Domain model validation, the JSON repository adapter, and ClaimsService."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.application.services import ClaimsService
from app.domain.exceptions import ClaimNotFoundError, InvalidClaimIdError
from app.domain.models.claim import ClaimSubmission
from app.infrastructure.persistence.json_claims_repository import JsonClaimsRepository


def read_claims(data_dir: Path) -> list[dict]:
    return json.loads((data_dir / "mock_claims.json").read_text(encoding="utf-8"))


# --- repository -------------------------------------------------------------------


def test_repository_lists_and_finds(claims_repo: JsonClaimsRepository) -> None:
    assert [c.claim_id for c in claims_repo.list_all()] == ["CLM-8821", "CLM-9014"]
    assert claims_repo.find_by_id("CLM-9014").status == "Under Review"
    assert claims_repo.find_by_id("CLM-0000") is None


def test_repository_add_appends_record(claims_repo: JsonClaimsRepository, data_dir: Path) -> None:
    submission = ClaimSubmission(
        policy_number="pol-1092",
        claim_type="water damage",
        amount=1500,
        description="Pipe burst under the kitchen sink and soaked the floor.",
    )

    claim = claims_repo.add(submission)

    assert claim.claim_id.startswith("CLM-") and len(claim.claim_id) == 8
    assert claim.status == "Submitted"
    assert claim.policy_number == "POL-1092"  # normalised
    assert claim.claim_type == "Water Damage"  # normalised

    on_disk = read_claims(data_dir)
    assert len(on_disk) == 3
    assert on_disk[-1]["claim_id"] == claim.claim_id
    assert on_disk[-1]["description"] == submission.description


def test_repository_requires_existing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        JsonClaimsRepository(tmp_path / "missing.json")


# --- service ----------------------------------------------------------------------


def test_service_get_status_normalises_id(claims_service: ClaimsService) -> None:
    claim = claims_service.get_status(" clm-8821 ")
    assert claim.policy_number == "POL-1092" and claim.status == "Approved"


def test_service_get_status_not_found(claims_service: ClaimsService) -> None:
    with pytest.raises(ClaimNotFoundError):
        claims_service.get_status("CLM-0000")


def test_service_get_status_invalid_format(claims_service: ClaimsService) -> None:
    with pytest.raises(InvalidClaimIdError, match="CLM-####"):
        claims_service.get_status("8821")


# --- domain validation ------------------------------------------------------------


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("policy_number", "1092"),
        ("policy_number", "POL-12"),
        ("claim_type", "Fire"),
        ("amount", 0),
        ("amount", -100),
        ("amount", "lots"),
        ("amount", 5_000_000),
        ("description", "short"),
    ],
)
def test_submission_validation_rejects_bad_input(field: str, value) -> None:
    payload = {
        "policy_number": "POL-1092",
        "claim_type": "Water Damage",
        "amount": 1500,
        "description": "Pipe burst under the kitchen sink.",
        field: value,
    }
    with pytest.raises(ValidationError):
        ClaimSubmission(**payload)


def test_submission_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ClaimSubmission(
            policy_number="POL-1092",
            claim_type="Water Damage",
            amount=10,
            description="A valid description here.",
            status="Approved",  # the LLM must not be able to set status
        )
