from __future__ import annotations

from app.autonomy.planner import DeterministicPlanner, Goal
from app.nostale_perception.game_state import GameState
from app.nostale_perception.network_decoder import DecodedObservation


def test_planner_selects_safe_baseline_for_valid_state() -> None:
    state = GameState.empty()
    state.apply(DecodedObservation("p", "player_info", {"entity_id": 1, "hp": 100, "hp_max": 100}, 0.9, "fixture"))
    trace = DeterministicPlanner().plan(state, Goal.OBSERVE_AREA)
    assert trace.state_valid is True
    assert trace.selected_skill == "observe_area"
    assert trace.candidates


def test_planner_blocks_invalid_state() -> None:
    state = GameState.empty()
    state.apply(DecodedObservation("p", "player_info", {"entity_id": 1, "hp": 101, "hp_max": 100}, 0.9, "fixture"))
    trace = DeterministicPlanner().plan(state, Goal.OBSERVE_AREA)
    assert trace.state_valid is False
    assert trace.selected_skill is None


def test_survival_goal_prefers_conservative_maintenance_when_hp_is_low() -> None:
    state = GameState.empty()
    state.apply(DecodedObservation("p", "player_info", {"entity_id": 1, "hp": 20, "hp_max": 100}, 0.9, "fixture"))
    trace = DeterministicPlanner().plan(state, Goal.SURVIVE)
    assert trace.selected_skill == "maintain_state"
    assert "health" in trace.reason
