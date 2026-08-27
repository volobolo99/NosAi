"""NosAi-owned intelligent memory boundary.

Memory is advisory input to planning. It cannot authorize an action.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class MemoryItem:
    kind: str
    payload: Mapping[str, Any]
    confidence: float = 1.0
    provenance: str = "unknown"


class MemoryStore(Protocol):
    async def write(self, item: MemoryItem) -> None: ...
    async def retrieve(self, query: Mapping[str, Any], limit: int = 20) -> list[MemoryItem]: ...


@dataclass
class IntelligentMemory:
    stores: dict[str, MemoryStore] = field(default_factory=dict)

    async def remember(self, item: MemoryItem) -> None:
        store = self.stores.get(item.kind)
        if store is None:
            raise ValueError(f"unsupported memory kind: {item.kind}")
        await store.write(item)

    async def context(self, query: Mapping[str, Any], limit: int = 20) -> list[MemoryItem]:
        result: list[MemoryItem] = []
        for store in self.stores.values():
            result.extend(await store.retrieve(query, limit))
        return result[:limit]
