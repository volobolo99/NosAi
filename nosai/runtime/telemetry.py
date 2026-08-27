"""Bounded, deterministic observation telemetry for G3.7."""
from __future__ import annotations

from dataclasses import dataclass
from time import monotonic


@dataclass(frozen=True)
class TelemetryEvent:
    sequence: int
    session_id: str
    kind: str
    action: str
    outcome: str
    elapsed_ms: float


class TelemetryCollector:
    """In-memory bounded telemetry collector; never authorizes execution."""

    def __init__(self, max_events: int = 512) -> None:
        if max_events < 1:
            raise ValueError("max_events must be positive")
        self._max = max_events
        self._events: list[TelemetryEvent] = []
        self._sequence = 0

    def record(self, session_id: str, kind: str, action: str, outcome: str, started_at: float | None = None) -> TelemetryEvent:
        if not session_id.strip():
            raise ValueError("session_id must be non-empty")
        if not kind.strip() or not action.strip() or not outcome.strip():
            raise ValueError("kind, action and outcome must be non-empty")
        self._sequence += 1
        elapsed_ms = 0.0 if started_at is None else max(0.0, (monotonic() - started_at) * 1000.0)
        event = TelemetryEvent(self._sequence, session_id, kind, action, outcome, elapsed_ms)
        self._events.append(event)
        if len(self._events) > self._max:
            del self._events[: len(self._events) - self._max]
        return event

    def events(self) -> tuple[TelemetryEvent, ...]:
        return tuple(self._events)

    def counts(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for event in self._events:
            result[event.kind] = result.get(event.kind, 0) + 1
        return result
