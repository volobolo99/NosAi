from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from app.client.adapter import ClientState
from app.dashboard.events import DashboardEventBus
from app.dashboard.runtime_bridge import RuntimeDashboardStreamer
from app.dashboard.server import app, set_runtime_adapter


class FakeClientAdapter:
    def __init__(self) -> None:
        self.closed = False
        self.tick = 0

    def check_connection(self) -> bool:
        return True

    def read_state(self) -> ClientState:
        self.tick += 1
        return ClientState(
            tick=self.tick,
            payload={"client": {"source": "test", "observation_only": True}},
        )

    def validate_action(self, action):
        return action is None

    def close(self) -> None:
        self.closed = True


def test_live_streamer_publishes_client_snapshots() -> None:
    async def scenario() -> None:
        adapter = FakeClientAdapter()
        bus = DashboardEventBus()
        queue = bus.subscribe()
        streamer = RuntimeDashboardStreamer(adapter, bus, interval_s=0.001, sessione="e2e")
        task = streamer.start()
        event = await asyncio.wait_for(queue.get(), timeout=1)
        await streamer.stop()
        bus.unsubscribe(queue)
        assert event.tipo == "snapshot"
        assert event.sessione == "e2e"
        assert event.dati["client"]["source"] == "test"
        assert event.dati["client"]["observation_only"] is True
        assert task.done()

    asyncio.run(scenario())


def test_dashboard_probe_endpoint_uses_observation_only_adapter() -> None:
    adapter = FakeClientAdapter()
    set_runtime_adapter(adapter)
    try:
        with TestClient(app) as client:
            response = client.get("/api/sonda-client")
        assert response.status_code == 200
        body = response.json()
        assert body == {
            "connesso": True,
            "stato_valido": True,
            "azione_valida": True,
            "dettaglio": "connected; state readable; dry-run validated",
        }
    finally:
        set_runtime_adapter(None)
