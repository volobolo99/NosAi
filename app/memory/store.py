"""Small local-first stores with deterministic JSON persistence.

The stores deliberately expose interfaces that can later be backed by SQLite,
a vector index, or another provider without changing NosAI contracts.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .models import MemoryItem, StateRecord, MemoryScope, MemoryType


class MemoryStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def put(self, item: MemoryItem) -> None:
        records = {entry.id: entry for entry in self.list()}
        records[item.id] = item
        self._write(records.values())

    def get(self, item_id: str) -> MemoryItem | None:
        return next((item for item in self.list() if item.id == item_id), None)

    def list(self, *, scope: MemoryScope | None = None, memory_type: MemoryType | None = None) -> list[MemoryItem]:
        if not self.path.exists():
            return []
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [
            MemoryItem(
                id=row["id"], memory_type=MemoryType(row["memory_type"]),
                scope=MemoryScope(row["scope"]), content=row["content"],
                created_at=row["created_at"], updated_at=row["updated_at"],
                provenance=tuple(row.get("provenance", ())), confidence=row.get("confidence", 1.0),
                metadata=row.get("metadata", {}),
            )
            for row in raw
            if (scope is None or row["scope"] == scope.value)
            and (memory_type is None or row["memory_type"] == memory_type.value)
        ]

    def _write(self, items: Iterable[MemoryItem]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(item) for item in sorted(items, key=lambda x: x.id)]
        self.path.write_text(json.dumps(payload, sort_keys=True, ensure_ascii=False, default=lambda x: x.value), encoding="utf-8")


class StateStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def save(self, state: StateRecord) -> None:
        records = {entry.run_id: entry for entry in self.list()}
        previous = records.get(state.run_id)
        if previous is not None and state.version < previous.version:
            raise ValueError("state version cannot move backwards")
        records[state.run_id] = state
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(entry) for entry in sorted(records.values(), key=lambda x: x.run_id)]
        self.path.write_text(json.dumps(payload, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def load(self, run_id: str) -> StateRecord | None:
        return next((entry for entry in self.list() if entry.run_id == run_id), None)

    def list(self) -> list[StateRecord]:
        if not self.path.exists():
            return []
        return [StateRecord(**row) for row in json.loads(self.path.read_text(encoding="utf-8"))]
