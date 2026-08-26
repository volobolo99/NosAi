"""Bridge the normalized client/runtime state into dashboard events.

The bridge is observation-only: it never executes a game action.
"""
from __future__ import annotations

import asyncio
from typing import Any

from .events import DashboardEvent, DashboardEventBus
from .state import snapshot_from_adapter


def publish_runtime_snapshot(adapter: Any, bus: DashboardEventBus, sessione: str = "runtime") -> DashboardEvent:
    snapshot = snapshot_from_adapter(adapter).to_dict()
    event = DashboardEvent(tipo="snapshot", sessione=sessione, dati=snapshot)
    bus.publish(event)
    return event


def publish_runtime_trace(adapter: Any, bus: DashboardEventBus, sessione: str = "runtime") -> list[DashboardEvent]:
    snapshot = snapshot_from_adapter(adapter).to_dict()
    decision = snapshot.get("decision", {})
    supplied = decision.get("trace") or decision.get("decision_trace") or []
    events: list[DashboardEvent] = []
    for index in range(1, 16):
        item = supplied[index - 1] if index <= len(supplied) else {"stato": "completato" if index < 15 else "in osservazione"}
        if not isinstance(item, dict):
            item = {"riepilogo": str(item)}
        event = DashboardEvent(tipo="traccia_modulo", sessione=sessione, dati={"modulo": f"M{index}", "riepilogo": item})
        bus.publish(event)
        events.append(event)
    return events


class RuntimeDashboardStreamer:
    """Continuously mirror a real ClientAdapter into the dashboard.

    The adapter remains the only source of client state. Every poll is
    non-destructive and failures are emitted as diagnostic events rather than
    terminating the dashboard process.
    """

    def __init__(self, adapter: Any, bus: DashboardEventBus, interval_s: float = 0.5, sessione: str = "runtime") -> None:
        if interval_s <= 0:
            raise ValueError("interval_s must be > 0")
        self.adapter = adapter
        self.bus = bus
        self.interval_s = interval_s
        self.sessione = sessione
        self._task: asyncio.Task[None] | None = None

    async def run(self) -> None:
        while True:
            try:
                publish_runtime_snapshot(self.adapter, self.bus, self.sessione)
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
