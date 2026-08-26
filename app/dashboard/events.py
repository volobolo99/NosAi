"""Structured runtime events consumed by the observability dashboard."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import asyncio
import json
from typing import Any


@dataclass(frozen=True)
class DashboardEvent:
    """Transport-neutral event; sensitive reasoning is represented as a summary."""

    tipo: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sessione: str = "default"
    dati: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, separators=(",", ":"))


class DashboardEventBus:
    """Small async pub/sub bridge between runtime modules and the dashboard."""

    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[DashboardEvent]] = set()

    def publish(self, event: DashboardEvent) -> None:
        for queue in tuple(self._subscribers):
            if not queue.full():
                queue.put_nowait(event)

    def subscribe(self, maxsize: int = 128) -> asyncio.Queue[DashboardEvent]:
        queue: asyncio.Queue[DashboardEvent] = asyncio.Queue(maxsize=maxsize)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[DashboardEvent]) -> None:
        self._subscribers.discard(queue)
