from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CycleTelemetry:
    cycle_id: str
    observation_id: str
    decision_id: str
    action_id: str
    safety_allowed: bool
    evaluation_accepted: bool
    reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


class InMemoryTelemetry:
    """Append-only deterministic sink for dry-run and tests."""

    def __init__(self) -> None:
        self._events: list[CycleTelemetry] = []

    def record(self, event: CycleTelemetry) -> None:
        self._events.append(event)

    def snapshot(self) -> tuple[CycleTelemetry, ...]:
        return tuple(self._events)
