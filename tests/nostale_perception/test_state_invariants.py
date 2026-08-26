from __future__ import annotations

from app.nostale_perception.game_state import GameState
from app.nostale_perception.network_decoder import DecodedObservation
from app.nostale_perception.state_invariants import validate_game_state


def test_valid_game_state_passes_invariants() -> None:
    state = GameState.empty()
    state.apply(DecodedObservation("p", "player_info", {"entity_id": 1, "hp": 90, "hp_max": 100, "mp": 20, "mp_max": 50}, 0.9, "fixture"))
    state.apply(DecodedObservation("m", "movement", {"entity_id": 2, "x": 10.0, "y": 20.0}, 0.9, "fixture"))
    validation = validate_game_state(state)
    assert validation.valid
    assert validation.errors == 0


def test_hp_over_max_is_error() -> None:
    state = GameState.empty()
    state.apply(DecodedObservation("p", "player_info", {"entity_id": 1, "hp": 101, "hp_max": 100}, 0.9, "fixture"))
    validation = validate_game_state(state)
    assert not validation.valid
    assert any(issue.code == "PLAYER_HP_OVER_MAX" for issue in validation.issues)


def test_nonfinite_world_coordinate_is_error() -> None:
    state = GameState.empty()
    state.apply(DecodedObservation("m", "movement", {"entity_id": 2, "x": float("nan"), "y": 20.0}, 0.9, "fixture"))
    validation = validate_game_state(state)
    assert not validation.valid
    assert any(issue.code == "ENTITY_X_NONFINITE" for issue in validation.issues)
