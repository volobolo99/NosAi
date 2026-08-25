"""Append-only persistence for versioned Test Pilot events."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import uuid

from .telemetry_schema import PilotTelemetryEvent, validate_event


class PilotEventStore:
    """Persist validated v1 events as one JSON object per line."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def record(
        self,
        event_type: str,
        session_id: str,
        *,
        tick: int | None = None,
        state_quality: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> PilotTelemetryEvent:
        event = PilotTelemetryEvent(
            event_type=event_type,
            session_id=session_id,
            event_id=uuid.uuid4().hex,
            tick=tick,
            state_quality=state_quality,
            payload=payload or {},
        )
        validate_event(event)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
        return event

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
