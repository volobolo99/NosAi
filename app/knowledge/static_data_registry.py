"""Validated, provenance-aware registry for imported NosTale static data."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class KnowledgeRecord:
    record_id: str
    kind: str
    fields: Mapping[str, Any]
    provenance: Mapping[str, Any]
    verified: bool = False


class StaticKnowledgeRegistry:
    """In-memory registry that refuses unverifiable promoted records."""

    def __init__(self) -> None:
        self._records: dict[tuple[str, str], KnowledgeRecord] = {}

    def add(self, record: KnowledgeRecord) -> None:
        if not record.record_id or not record.kind:
            raise ValueError("record_id and kind are required")
        if not record.provenance.get("source"):
            raise ValueError("source provenance is required")
        self._records[(record.kind, record.record_id)] = record

    def promote_verified(self, kind: str, record_id: str) -> KnowledgeRecord:
        key = (kind, record_id)
        record = self._records.get(key)
        if record is None:
            raise KeyError(key)
        promoted = KnowledgeRecord(
            record_id=record.record_id,
            kind=record.kind,
            fields=dict(record.fields),
            provenance=dict(record.provenance),
            verified=True,
        )
        self._records[key] = promoted
        return promoted

    def get_verified(self, kind: str, record_id: str) -> KnowledgeRecord | None:
        record = self._records.get((kind, record_id))
        return record if record and record.verified else None

    def __len__(self) -> int:
        return len(self._records)
