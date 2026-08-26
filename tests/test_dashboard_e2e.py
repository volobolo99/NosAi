from __future__ import annotations

import asyncio

from app.client.adapter import ClientState
from app.dashboard.events import DashboardEventBus
from app.dashboard.nosapki import parse_item_html
from app.dashboard.runtime_bridge import publish_runtime_snapshot, publish_runtime_trace


class FakeAdapter:
    def check_connection(self) -> bool:
        return True

    def read_state(self) -> ClientState:
        return ClientState(
            tick=42,
            payload={
                "client": {"connected": True},
                "world": {"mappa": "NosVille", "posizione": [120, 88]},
                "inventory": [{"id": "gemma-1", "nome": "Gemma", "image_url": "https://nosapki.com/img/gemma.png"}],
                "goal": {"nome": "Raccogliere materiali"},
                "decision": {
                    "azione": "ATTACK",
                    "confidence": 0.91,
                    "trace": [{"stato": f"checkpoint-{i}"} for i in range(1, 16)],
                },
                "performance": {"decision_ms": 12},
            },
        )

    def validate_action(self, action: object) -> bool:
        return False

    def close(self) -> None:
        return None


def test_end_to_end_runtime_snapshot_and_m15_trace() -> None:
    bus = DashboardEventBus()
    queue = bus.subscribe()
    adapter = FakeAdapter()

    snapshot = publish_runtime_snapshot(adapter, bus, sessione="e2e")
    trace = publish_runtime_trace(adapter, bus, sessione="e2e")

    received = [asyncio.run(queue.get()) for _ in range(16)]
    bus.unsubscribe(queue)

    assert snapshot.tipo == "snapshot"
    assert snapshot.dati["tick"] == 42
    assert snapshot.dati["inventory"][0]["id"] == "gemma-1"
    assert len(trace) == 15
    assert received[0]["tipo"] == "snapshot"
    assert [event["dati"]["modulo"] for event in received[1:]] == [f"M{i}" for i in range(1, 16)]


def test_nosapki_html_connector_extracts_safe_item_image() -> None:
    html = '''<html><head><title>Gemma</title>
    <meta property="og:title" content="Gemma preziosa">
    <meta property="og:image" content="/img/gemma.png"></head></html>'''
    item = parse_item_html(html, "https://nosapki.com/it/items/example")
    assert item.nome == "Gemma preziosa"
    assert item.immagine_url == "https://nosapki.com/img/gemma.png"


def test_nosapki_connector_rejects_external_image() -> None:
    html = '''<meta property="og:title" content="Oggetto">
    <meta property="og:image" content="https://evil.example/x.png">'''
    item = parse_item_html(html, "https://nosapki.com/it/items/example")
    assert item.immagine_url is None
