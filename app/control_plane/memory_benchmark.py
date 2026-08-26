"""Deterministic retrieval metrics for the NosAi memory benchmark."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True, slots=True)
class RetrievalCase:
    query: str
    relevant_ids: frozenset[str]


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    query: str
    returned_ids: tuple[str, ...]


def recall_at_k(cases: Sequence[RetrievalCase], results: Sequence[RetrievalResult], k: int) -> float:
    if len(cases) != len(results) or not cases:
        raise ValueError("cases and results must have equal, non-zero lengths")
    if k <= 0:
        raise ValueError("k must be positive")
    total = 0.0
    for case, result in zip(cases, results):
        if not case.relevant_ids:
            continue
        found = set(result.returned_ids[:k]) & set(case.relevant_ids)
        total += len(found) / len(case.relevant_ids)
    return total / len(cases)


def precision_at_k(cases: Sequence[RetrievalCase], results: Sequence[RetrievalResult], k: int) -> float:
    if len(cases) != len(results) or not cases:
        raise ValueError("cases and results must have equal, non-zero lengths")
    if k <= 0:
        raise ValueError("k must be positive")
    total = 0.0
    for case, result in zip(cases, results):
        returned = result.returned_ids[:k]
        if not returned:
            continue
        total += len(set(returned) & set(case.relevant_ids)) / len(returned)
    return total / len(cases)
