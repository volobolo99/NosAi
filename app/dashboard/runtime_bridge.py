"""Bridge the normalized client/runtime state into dashboard events.

The bridge is observation-only: it never executes a game action.
"""
from __future__ import annotations

from typing import Any

from .events import DashboardEvent, DashboardEventBus
from .state import snapshot_from_adapter


def publish_runtime_snapshot(adapter: Any, bus: DashboardEventBus, sessione: str = "runtime") -> DashboardEvent:
    """Read one normalized adapter snapshot and publish it to the dashboard."""
    snapshot = snapshot_from_adapter(adapter).to_dict()
    event = DashboardEvent(tipo="snapshot", sessione=sessione, dati=snapshot)
    bus.publish(event)
    return event


def publish_runtime_trace(adapter: Any, bus: DashboardEventBus, sessione: str = "runtime") -> list[DashboardEvent]:
    """Publish safe structured M1-M15 trace events without inventing runtime data."""
    snapshot = snapshot_from_adapter(adapter).to_dict()
    decision = snapshot.get("decision", {})
    supplied = decision.get("trace") or decision.get("decision_trace") or []
    events: list[DashboardEvent] = []
    for index in range(1, 16):
        has_runtime_trace = index <= len(supplied)
        item = supplied[index - 1] if has_runtime_trace else {"stato": "non disponibile"}
        if not isinstance(item, dict):
            item = {"riepilogo": str(item)}
        event = DashboardEvent(
            tipo="traccia_modulo",
            sessione=sessione,
            dati={
                "modulo": f"M{index}",
                "riepilogo": item,
                "fonte_trace": "runtime" if has_runtime_trace else "non_disponibile",
            },
        )
        bus.publish(event)
        events.append(event)
    return events
