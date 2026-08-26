"""Bridge the normalized client/runtime state into dashboard events.

The bridge is observation-only: it never executes a game action.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

from .catalog import ItemCatalog
from .events import DashboardEvent, DashboardEventBus
from .state import snapshot_from_adapter


def publish_runtime_snapshot(adapter: Any, bus: DashboardEventBus, sessione: str = "runtime") -> DashboardEvent:
    snapshot = snapshot_from_adapter(adapter).to_dict()
    event = DashboardEvent(tipo="snapshot", sessione=sessione, dati=snapshot)
    bus.publish(event)
    return event


def publish_runtime_trace(adapter: Any, bus: DashboardEventBus, sessione: str = "runtime") -> list[DashboardEvent]:
    """Publish the real M1-M15 trace without inventing unavailable details."""
    snapshot = snapshot_from_adapter(adapter).to_dict()
    decision = snapshot.get("decision", {})
    supplied = decision.get("trace") or decision.get("decision_trace") or []
    has_trace = isinstance(supplied, list) and bool(supplied)
    events: list[DashboardEvent] = []
    for index in range(1, 16):
        item = supplied[index - 1] if has_trace and index <= len(supplied) else {
            "stato": "non disponibile",
            "fonte": "runtime senza traccia M1-M15",
        }
        if not isinstance(item, dict):
            item = {"riepilogo": str(item)}
        event = DashboardEvent(
            tipo="traccia_modulo",
            sessione=sessione,
            dati={
                "modulo": f"M{index}",
                "riepilogo": item,
                "fonte_trace": "runtime" if has_trace else "non_disponibile",
            },
        )
        bus.publish(event)
        events.append(event)
    return events


class RuntimeDashboardStreamer:
    """Continuously mirror a real ClientAdapter into the dashboard.

    The adapter remains the only source of client state. Every poll is
    non-destructive. Inventory items are enriched through the catalog when
    available, and the M1-M15 trace is emitted only when it changes.
    """

    def __init__(
        self,
        adapter: Any,
        bus: DashboardEventBus,
        interval_s: float = 0.5,
        sessione: str = "runtime",
        catalog: ItemCatalog | None = None,
    ) -> None:
        if interval_s <= 0:
            raise ValueError("interval_s must be > 0")
        self.adapter = adapter
        self.bus = bus
        self.interval_s = interval_s
        self.sessione = sessione
        self.catalog = catalog
        self._task: asyncio.Task[None] | None = None
        self._last_trace_key: str | None = None

    @staticmethod
    def _trace_key(snapshot: dict[str, Any]) -> str:
        decision = snapshot.get("decision", {})
        trace = decision.get("trace") or decision.get("decision_trace") or []
        return json.dumps(trace, ensure_ascii=False, sort_keys=True, default=str)

    def _enrich_inventory(self, snapshot: dict[str, Any]) -> None:
        if self.catalog is None:
            return
        for item in snapshot.get("inventory", []):
            if isinstance(item, dict):
                try:
                    self.catalog.enrich_observed(item)
                except (OSError, ValueError, UnicodeError):
                    continue

    async def run(self) -> None:
        while True:
            try:
                snapshot_event = publish_runtime_snapshot(self.adapter, self.bus, self.sessione)
                snapshot = snapshot_event.dati
                self._enrich_inventory(snapshot)
                trace_key = self._trace_key(snapshot)
                if trace_key != self._last_trace_key:
                    publish_runtime_trace(self.adapter, self.bus, self.sessione)
                    self._last_trace_key = trace_key
            except Exception as exc:  # defensive boundary around optional live clients
                self.bus.publish(DashboardEvent(
                    tipo="errore_runtime",
                    sessione=self.sessione,
                    dati={"messaggio": str(exc), "observation_only": True},
                ))
            await asyncio.sleep(self.interval_s)

    def start(self) -> asyncio.Task[None]:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self.run(), name="nosai-dashboard-runtime")
        return self._task

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
