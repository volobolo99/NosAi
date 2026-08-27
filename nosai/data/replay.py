"""Deterministic replay and quality validation for AI datasets (G3.18)."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class ReplayResult:
    session_id: str
    records: int
    digest: str


class DatasetReplay:
    """Replays observation records without invoking runtime actions."""

    def replay(self, session_id: str, records: list[dict[str, object]]) -> ReplayResult:
        if not session_id.strip():
            raise ValueError("session_id must be non-empty")
        if not records:
            raise ValueError("records must be non-empty")
        canonical = json.dumps(records, sort_keys=True, separators=(",", ":"), default=str)
        digest = sha256(f"{session_id}|{canonical}".encode()).hexdigest()
        return ReplayResult(session_id, len(records), digest)

    def quality_report(self, records: list[dict[str, object]]) -> dict[str, int]:
        if not isinstance(records, list):
            raise ValueError("records must be a list")
        valid = sum(1 for record in records if isinstance(record, dict) and bool(record))
        return {"total": len(records), "valid": valid, "invalid": len(records) - valid}
