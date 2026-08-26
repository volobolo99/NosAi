from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CycleTelemetry:
    """Append-only evidence emitted for one gated ZMSIA cycle."""

    cycle_id: str
    observation_id: str
    decision_id: str
    action_id: str
    action_type: str
    safety_allowed: bool
    evaluation_accepted: bool
    reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


class InMemoryTelemetry:
    """Append-only deterministic sink for dry-run and tests."""

    def __init__(self) -> None:
        """Create an empty telemetry sink."""
        self._events: list[CycleTelemetry] = []

    def record(self, event: CycleTelemetry) -> None:
        """Append one immutable telemetry event to the sink."""
        self._events.append(event)

    def snapshot(self) -> tuple[CycleTelemetry, ...]:
        """Return an immutable point-in-time view of recorded events."""
        return tuple(self._events)
