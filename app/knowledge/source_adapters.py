"""Source adapters for verified external knowledge.

Adapters return candidates with immutable provenance. They never promote data by
virtue of being present in a source; validation/promotion remains a separate step.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class KnowledgeCandidate:
    record_id: str
    kind: str
    fields: Mapping[str, Any]
    source_id: str
    source_ref: str
    source_version: str | None = None
    source_commit: str | None = None
    verified: bool = False


def candidates_from_records(
    records: Iterable[Mapping[str, Any]],
    *,
    source_id: str,
    source_ref: str,
    source_version: str | None = None,
    source_commit: str | None = None,
) -> list[KnowledgeCandidate]:
    result: list[KnowledgeCandidate] = []
    for record in records:
        record_id = record.get("id")
        kind = record.get("kind")
        fields = record.get("fields")
        if not isinstance(record_id, str) or not record_id:
            raise ValueError("candidate id is required")
        if not isinstance(kind, str) or not kind:
            raise ValueError("candidate kind is required")
        if not isinstance(fields, Mapping):
            raise ValueError("candidate fields must be a mapping")
        result.append(
            KnowledgeCandidate(
                record_id=record_id,
                kind=kind,
                fields=dict(fields),
                source_id=source_id,
                source_ref=source_ref,
                source_version=source_version,
                source_commit=source_commit,
            )
        )
    return result
