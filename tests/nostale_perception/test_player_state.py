from __future__ import annotations

from app.nostale_perception.network_observation import NetworkObservation
from app.nostale_perception.player_decoders import decode_c_info, decode_cond
from app.nostale_perception.player_state import PlayerState


def obs(header: str, payload: bytes) -> NetworkObservation:
    return NetworkObservation("o1", 1, "recv", header, payload, "fixture", "1")


def test_player_info_projection() -> None:
    decoded = decode_c_info(obs("c_info", b"42 100 200 50 100"))
    state = PlayerState()
    assert decoded is not None and state.apply(decoded)
    assert (state.entity_id, state.hp, state.hp_max, state.mp, state.mp_max) == (42, 100, 200, 50, 100)


def test_condition_projection_and_invalid_info() -> None:
    state = PlayerState()
    decoded = decode_cond(obs("cond", b"stunned"))
    assert decoded is not None and state.apply(decoded)
    assert state.condition == "stunned"
    assert decode_c_info(obs("c_info", b"42 300 200 1 2")) is None
