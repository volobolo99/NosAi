"""Bridge the normalized client/runtime state into dashboard events.

The bridge is observation-only: it never executes a game action.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from .catalog import ItemCatalog
from .events import DashboardEvent, DashboardEventBus
from .state import snapshot_from_adapter

LOGGER = logging.getLogger(__name__)


def _publish_trace_snapshot(snapshot: dict[str, Any], bus: DashboardEventBus, sessione: str) -> list[DashboardEvent]:
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


def publish_runtime_snapshot(adapter: Any, bus: DashboardEventBus, sessione: str = "runtime") -> DashboardEvent:
    snapshot = snapshot_from_adapter(adapter).to_dict()
    event = DashboardEvent(tipo="snapshot", sessione=sessione, dati=snapshot)
    bus.publish(event)
    return event


def publish_runtime_trace(adapter: Any, bus: DashboardEventBus, sessione: str = "runtime") -> list[DashboardEvent]:
    """Publish the real M1-M15 trace from one normalized adapter read."""
    snapshot = snapshot_from_adapter(adapter).to_dict()
    return _publish_trace_snapshot(snapshot, bus, sessione)


class RuntimeDashboardStreamer:
    """Continuously mirror a real ClientAdapter into dashboard events.

    All adapter reads remain observation-only. Blocking catalog/network work is
    moved to worker threads so the asyncio event loop stays responsive.
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
        self._enrichment_cache: set[str] = set()

    @staticmethod
    def _trace_key(snapshot: dict[str, Any]) -> str:
        decision = snapshot.get("decision", {})
        trace = decision.get("trace") or decision.get("decision_trace") or []
        return json.dumps(trace, ensure_ascii=False, sort_keys=True, default=str)

    async def _enrich_inventory(self, snapshot: dict[str, Any]) -> None:
        if self.catalog is None:
            return
        jobs = []
        for item in snapshot.get("inventory", []):
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id") or item.get("item_id") or "").strip()
            source_url = str(item.get("fonte_url") or item.get("source_url") or "").strip()
            cache_key = f"{item_id}|{source_url}"
            if item_id and source_url and cache_key not in self._enrichment_cache:
                self._enrichment_cache.add(cache_key)
                jobs.append(asyncio.to_thread(self.catalog.enrich_observed, item))
        if jobs:
            results = await asyncio.gather(*jobs, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    LOGGER.warning("arricchimento item non riuscito: %s", type(result).__name__)

    async def run(self) -> None:
        while True:
            try:
                snapshot_event = publish_runtime_snapshot(self.adapter, self.bus, self.sessione)
                snapshot = snapshot_event.dati
                await self._enrich_inventory(snapshot)
                trace_key = self._trace_key(snapshot)
                if trace_key != self._last_trace_key:
                    _publish_trace_snapshot(snapshot, self.bus, self.sessione)
                    self._last_trace_key = trace_key
            except Exception:
                LOGGER.exception("errore durante la sincronizzazione dashboard")
                self.bus.publish(DashboardEvent(
                    tipo="errore_runtime",
                    sessione=self.sessione,
                    dati={"messaggio": "errore durante la sincronizzazione del client", "observation_only": True},
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
