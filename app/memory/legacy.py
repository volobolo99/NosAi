"""Backward-compatible episodic memory API.

This adapter preserves the pre-G3 ``EpisodicMemory`` and ``MemoryQuery``
contracts while the new provider-neutral G3 memory stores evolve separately.
It intentionally keeps the legacy API in its own module so the new MemoryStore
and StateStore contracts remain clean and replaceable.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from app.ai.contracts import MemoryRecord


@dataclass(frozen=True)
class MemoryQuery:
    state_fingerprint: str | None = None
    goal_kind: str | None = None
    limit: int = 10


class EpisodicMemory:
    """Bounded append-oriented compatibility memory with deterministic retrieval."""

    def __init__(self, capacity: int = 10_000):
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self._capacity = capacity
        self._records: list[MemoryRecord] = []

    @property
    def capacity(self) -> int:
        return self._capacity

    def __len__(self) -> int:
        return len(self._records)

    def append(self, record: MemoryRecord) -> None:
        if not isinstance(record, MemoryRecord):
            raise TypeError("record must be a MemoryRecord")
        self._records.append(record)
        overflow = len(self._records) - self._capacity
        if overflow > 0:
            del self._records[:overflow]

    def extend(self, records: Iterable[MemoryRecord]) -> None:
        for record in records:
            self.append(record)

    def query(self, query: MemoryQuery) -> Sequence[MemoryRecord]:
        if query.limit < 1:
            return ()
        matches = self._records
        if query.state_fingerprint is not None:
            matches = [r for r in matches if r.state_fingerprint == query.state_fingerprint]
        if query.goal_kind is not None:
            matches = [r for r in matches if r.goal.kind == query.goal_kind]
        return tuple(matches[-query.limit:][::-1])

    def recent(self, limit: int = 10) -> Sequence[MemoryRecord]:
        return self.query(MemoryQuery(limit=limit))

    def clear(self) -> None:
        self._records.clear()
