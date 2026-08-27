"""Provider-neutral intelligent memory facade.

The existing persistence layer remains authoritative. This facade adds typed
namespaces and provenance without coupling Brain to storage.
"""
from __future__ import annotations

from app.ai.contracts import MemoryRecord


class IntelligentMemory:
    NAMESPACES = ("working", "episodic", "semantic", "strategic")

    def __init__(self, store):
        self.store = store

    async def remember(self, namespace: str, record: MemoryRecord) -> None:
        if namespace not in self.NAMESPACES:
            raise ValueError(f"unsupported memory namespace: {namespace}")
        await self.store.write(namespace, record)

    async def recall(self, query: dict, limit: int = 20):
        return await self.store.search(query, limit=limit)
