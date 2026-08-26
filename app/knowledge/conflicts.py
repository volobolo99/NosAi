"""Detect disagreements between knowledge sources without choosing silently."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .source_adapters import KnowledgeCandidate


@dataclass(frozen=True)
class KnowledgeConflict:
    record_id: str
    kind: str
    field: str
    values: tuple[tuple[str, Any], ...]


def detect_conflicts(candidates: Iterable[KnowledgeCandidate]) -> list[KnowledgeConflict]:
    grouped: dict[tuple[str, str, str], list[tuple[str, Any]]] = {}
    for candidate in candidates:
        for field, value in candidate.fields.items():
            grouped.setdefault((candidate.record_id, candidate.kind, field), []).append(
                (candidate.source_id, value)
            )
    conflicts: list[KnowledgeConflict] = []
    for (record_id, kind, field), values in grouped.items():
        unique = {repr(value) for _, value in values}
        if len(unique) > 1:
            conflicts.append(KnowledgeConflict(record_id, kind, field, tuple(values)))
    return conflicts
