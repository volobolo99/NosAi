from app.integrations.canonical_state import CanonicalGameState
from app.integrations.state_builder import build_state


def test_empty_state_is_safe():
    state = CanonicalGameState.empty(1000, 42)
    assert state.client_pid == 42
    assert state.quality == 0.0
    assert state.entities == ()


def test_builder_normalizes_observation():
    state = build_state(
        timestamp_ms=1234,
        client_pid=99,
        sequence=7,
        frame_sha256="abc",
        observation={
            "map_id": "test-map",
            "packets_observed": 12,
            "sources": ["window", "replay"],
            "player": {"entity_id": "p1", "x": "12.5", "y": 8, "hp": "100", "max_hp": 100},
            "entities": [{"entity_id": "m1", "kind": "monster", "x": 15, "y": 9}],
        },
    )
    assert state.player.x == 12.5
    assert state.player.hp == 100
    assert state.entities[0].entity_id == "m1"
    assert state.packets_observed == 12
    assert state.sequence == 7
    assert state.quality == 1.0
