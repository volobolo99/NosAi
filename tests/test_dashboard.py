from __future__ import annotations

import asyncio

from app.client.adapter import ClientState
from app.dashboard.events import DashboardEvent, DashboardEventBus
from app.dashboard.state import snapshot_from_adapter
from app.dashboard.sources import image_reference


class Adapter:
    def check_connection(self) -> bool:
        return True

    def read_state(self) -> ClientState:
        return ClientState(
            tick=7,
            payload={
                "world": {"map": "test"},
                "inventory": [{"id": "item-1", "image_url": "https://example.test/item.png"}],
                "goal": {"name": "test"},
                "decision": {"confidence": 0.9},
                "performance": {"decision_ms": 4},
            },
        )

    def validate_action(self, action: object) -> bool:
        return False

    def close(self) -> None:
        return None


def test_dashboard_snapshot_uses_normalized_client_state() -> None:
    snapshot = snapshot_from_adapter(Adapter())
    assert snapshot.connected is True
    assert snapshot.tick == 7
    assert snapshot.world["map"] == "test"
    assert snapshot.inventory[0]["id"] == "item-1"


def test_event_bus_publishes_without_blocking() -> None:
    bus = DashboardEventBus()
    queue = bus.subscribe()
    event = DashboardEvent(tipo="decisione", dati={"confidence": 0.9})
    bus.publish(event)
    received = asyncio.run(queue.get())
    assert received.tipo == "decisione"
    assert received.dati["confidence"] == 0.9
    bus.unsubscribe(queue)


def test_image_reference_only_accepts_http_urls() -> None:
    assert image_reference({"image_url": "https://example.test/a.png"})
    assert image_reference({"image_url": "javascript:bad"}) is None
    assert image_reference({"image_url": None}) is None
