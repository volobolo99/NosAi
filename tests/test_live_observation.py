from __future__ import annotations

from app.client.adapter import ClientState
from app.client.live_observation import LiveObservation
from app.client.windows_hud import HudObservation


class FakeAdapter:
    def check_connection(self) -> bool:
        return True

    def read_state(self) -> ClientState:
        return ClientState(tick=42, payload={"window_rect": {"left": 0, "top": 0, "right": 800, "bottom": 600, "width": 800, "height": 600}})


def test_live_observation_preserves_observation_boundary(monkeypatch) -> None:
    class FakeFrame:
        png = b"png"
        width = 800
        height = 600
        source = "test-frame"
        observation_only = True

    class FakePerception:
        def __init__(self, adapter):
            self.adapter = adapter

        def capture(self):
            return FakeFrame()

    monkeypatch.setattr("app.client.live_observation.WindowsNosTalePerception", FakePerception)
    monkeypatch.setattr("app.client.live_observation.WindowsHudOcr.extract", lambda self, frame: HudObservation("HP: 100 MP: 50", hp=100, mp=50))
    world, frame = LiveObservation(FakeAdapter()).capture()
    assert world["observation_only"] is True
    assert world["hud"]["hp"] == 100
    assert world["frame"]["width"] == 800
    assert world["quality"]["hud_ocr"] == "PASS"
    assert frame == b"png"
    assert "action" not in world
