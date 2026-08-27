"""Validated, bounded recorder for live observer snapshots (G3.15)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json


@dataclass(frozen=True)
class DatasetRecord:
    record_id: str
    session_id: str
    observed_at: str
    payload: dict[str, object]


class LiveDatasetRecorder:
    """Append-only bounded recorder; stores observations, never actions."""

    def __init__(self, max_records: int = 10_000) -> None:
        if max_records < 1:
            raise ValueError("max_records must be positive")
        self._max = max_records
        self._records: list[DatasetRecord] = []

    def append(self, session_id: str, payload: dict[str, object], *, observed_at: datetime | None = None) -> DatasetRecord:
        if not session_id.strip():
            raise ValueError("session_id must be non-empty")
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload must be a non-empty mapping")
        timestamp = observed_at or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        record_id = hashlib.sha256(f"{session_id}|{timestamp.isoformat()}|{canonical}".encode()).hexdigest()
        record = DatasetRecord(record_id, session_id, timestamp.astimezone(timezone.utc).isoformat(), dict(payload))
        self._records.append(record)
        if len(self._records) > self._max:
            del self._records[: len(self._records) - self._max]
        return record

    def records(self) -> tuple[DatasetRecord, ...]:
        return tuple(self._records)

    def quality(self) -> dict[str, int]:
        total = len(self._records)
        sessions = len({record.session_id for record in self._records})
        return {"records": total, "sessions": sessions}
