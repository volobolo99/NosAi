"""Validate, conflict-check and promote knowledge candidates."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .conflicts import KnowledgeConflict, detect_conflicts
from .source_adapters import KnowledgeCandidate


@dataclass(frozen=True)
class ImportResult:
    accepted: tuple[KnowledgeCandidate, ...]
    quarantined: tuple[KnowledgeCandidate, ...]
    conflicts: tuple[KnowledgeConflict, ...]


def import_candidates(candidates: Iterable[KnowledgeCandidate], *, require_verified: bool = True) -> ImportResult:
    items = tuple(candidates)
    conflicts = tuple(detect_conflicts(items))
    conflict_ids = {c.record_id for c in conflicts}
    accepted: list[KnowledgeCandidate] = []
    quarantined: list[KnowledgeCandidate] = []
    for item in items:
        if item.record_id in conflict_ids or (require_verified and not item.verified):
            quarantined.append(item)
        else:
            accepted.append(item)
    return ImportResult(tuple(accepted), tuple(quarantined), conflicts)
