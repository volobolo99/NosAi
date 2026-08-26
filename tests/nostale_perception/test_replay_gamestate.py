from __future__ import annotations

from app.nostale_perception.network_decoder import DecodedObservation
from app.nostale_perception.replay_gamestate import replay_into_game_state


def test_replay_builds_state_and_reports_rejected_observations() -> None:
    observations = [
        DecodedObservation("p", "player_info", {"entity_id": 1, "hp": 90, "hp_max": 100}, 0.9, "fixture"),
        DecodedObservation("bad", "movement", {"entity_id": 2, "x": "bad", "y": 2}, 0.9, "fixture"),
        DecodedObservation("m", "movement", {"entity_id": 2, "x": 10.0, "y": 20.0}, 0.9, "fixture"),
    ]
    result = replay_into_game_state(observations)
    assert result.observations == 3
    assert result.applied == 2
    assert result.rejected == 1
    assert result.valid
    assert result.state.player.entity_id == 1
    assert result.state.world.entities[2].x == 10.0
