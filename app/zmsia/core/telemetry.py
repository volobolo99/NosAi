from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class CycleTelemetry:
    cycle_id: str
    timestamp: datetime
    observation_id: str
    decision_id: str
    action_type: str
    safety_allowed: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class InMemoryTelemetry:
    """Deterministic telemetry sink for tests and dry-run execution."""

    def __init__(self) -> None:
        self._events: list[CycleTelemetry] = []

    def record(self, event: CycleTelemetry) -> None:
        self._events.append(event)

    def snapshot(self) -> tuple[CycleTelemetry, ...]:
        return tuple(self._events)

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)
