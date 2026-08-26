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
    """Publish a safe, structured decision trace for the M1-M15 pipeline.

    Runtime-provided trace entries are marked as ``runtime``. Missing entries
    are explicit ``non_disponibile`` placeholders and are never presented as
    observations that came from the client.
    """
    snapshot = snapshot_from_adapter(adapter).to_dict()
    decision = snapshot.get("decision", {})
    supplied = decision.get("trace") or decision.get("decision_trace") or []
    events: list[DashboardEvent] = []
    for index in range(1, 16):
        if index <= len(supplied):
            item = supplied[index - 1]
            if not isinstance(item, dict):
                item = {"riepilogo": str(item)}
            source = "runtime"
        else:
            item = {"stato": "non disponibile"}
            source = "non_disponibile"
        event = DashboardEvent(
            tipo="traccia_modulo",
            sessione=sessione,
            dati={"modulo": f"M{index}", "riepilogo": item, "fonte_trace": source},
        )
        bus.publish(event)
        events.append(event)
    return events
