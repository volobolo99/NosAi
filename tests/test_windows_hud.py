from __future__ import annotations

from app.client.windows_hud import HudObservation
from app.client.world_state import VisualWorldState


def test_hud_observation_is_read_only() -> None:
    obs = HudObservation(text="HP: 1234 MP: 567 LV: 99", hp=1234, mp=567, level=99)
    assert obs.hp == 1234
    assert obs.mp == 567
    assert obs.level == 99
    assert obs.observation_only is True


def test_visual_world_state_serializes_without_actions() -> None:
    obs = HudObservation(text="HP: 100", hp=100)
    state = VisualWorldState(client={"pid": 1}, hud=obs)
    data = state.to_dict()
    assert data["client"]["pid"] == 1
    assert data["hud"]["hp"] == 100
    assert data["observation_only"] is True
    assert "action" not in data
