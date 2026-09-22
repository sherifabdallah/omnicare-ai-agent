"""ClaimsRepository adapter backed by a JSON file (the mock claims database).

The only code that touches mock_claims.json, so file format, locking and
atomic writes live in one place. Swap for a SQL implementation by writing
another class that satisfies the ClaimsRepository port.
"""

from __future__ import annotations

import json
import random
import threading
from pathlib import Path

from app.domain.models.claim import Claim, ClaimSubmission


class JsonClaimsRepository:
    def __init__(self, path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f"Claims database not found: {path}")
        self._path = path
        self._lock = threading.Lock()

    # --- ClaimsRepository port -----------------------------------------------

    def list_all(self) -> list[Claim]:
        with self._lock:
            return self._read()

    def find_by_id(self, claim_id: str) -> Claim | None:
        with self._lock:
            return next((c for c in self._read() if c.claim_id == claim_id), None)

    def add(self, submission: ClaimSubmission) -> Claim:
        with self._lock:
            claims = self._read()
            claim = Claim(
                claim_id=self._new_claim_id({c.claim_id for c in claims}),
                status="Submitted",
                **submission.model_dump(),
            )
            claims.append(claim)
            self._write(claims)
            return claim

    # --- internals -------------------------------------------------------------

    def _read(self) -> list[Claim]:
        raw = json.loads(self._path.read_text(encoding="utf-8") or "[]")
        return [Claim.model_validate(item) for item in raw]

    def _write(self, claims: list[Claim]) -> None:
        payload = [c.model_dump(exclude_none=True) for c in claims]
        tmp = self._path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(self._path)  # atomic on POSIX and Windows

    @staticmethod
    def _new_claim_id(existing: set[str]) -> str:
        while True:
            candidate = f"CLM-{random.randint(1000, 9999)}"
            if candidate not in existing:
                return candidate
