"""Versioned, append-only telemetry contract for Test Pilot v0.1."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

SCHEMA_VERSION = "pilot.telemetry.v1"


class PilotEventType(str, Enum):
    SESSION_STARTED = "session_started"
    STATE_OBSERVED = "state_observed"
    DECISION_PROPOSED = "decision_proposed"
    DECISION_BLOCKED = "decision_blocked"
    ACTION_VALIDATED = "action_validated"
    ERROR = "error"
    SESSION_FINISHED = "session_finished"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class PilotTelemetryEvent:
    """Stable event envelope; payload fields remain JSON-compatible."""

    event_type: PilotEventType
    session_id: str
    event_id: str
    tick: int | None = None
    state_quality: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    observed_at: str = field(default_factory=_now)
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "event_type": self.event_type.value,
            "event_id": self.event_id,
            "session_id": self.session_id,
            "tick": self.tick,
            "state_quality": self.state_quality,
            "payload": self.payload,
            "observed_at": self.observed_at,
        }


def validate_event(event: PilotTelemetryEvent) -> None:
    """Reject malformed events before they enter the diagnostic dataset."""

    if event.schema_version != SCHEMA_VERSION:
        raise ValueError(f"unsupported telemetry schema: {event.schema_version}")
    if not event.session_id.strip() or not event.event_id.strip():
        raise ValueError("session_id and event_id are required")
    if event.tick is not None and event.tick < 0:
        raise ValueError("tick must be non-negative")
    if not isinstance(event.payload, dict):
        raise ValueError("payload must be an object")
    if event.state_quality is not None and event.state_quality not in {
        "valid", "degraded", "unusable"
    }:
        raise ValueError(f"invalid state_quality: {event.state_quality}")
