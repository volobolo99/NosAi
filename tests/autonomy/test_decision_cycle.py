from __future__ import annotations

from app.autonomy.decision_cycle import DeterministicDecisionCycle
from app.autonomy.planner import Goal
from app.nostale_perception.autonomy import AutonomyLevel
from app.nostale_perception.game_state import GameState
from app.nostale_perception.network_decoder import DecodedObservation
from app.nostale_perception.simulated_executor import SimulatedSkillExecutor, SimulationRule


def _state(hp: int = 100) -> GameState:
    state = GameState.empty()
    state.apply(DecodedObservation("p", "player_info", {"entity_id": 1, "hp": hp, "hp_max": 100}, 0.9, "fixture"))
    return state


def test_full_cycle_executes_only_in_simulation() -> None:
    executor = SimulatedSkillExecutor([SimulationRule("observe_area", True, "ok")])
    cycle = DeterministicDecisionCycle(executor, AutonomyLevel.ASSISTED)
    result = cycle.run(_state(), Goal.OBSERVE_AREA)
    assert result.outcome == "success"
    assert result.execution.executed is True
    assert executor.executions == ["observe_area"]


def test_gateway_blocks_at_observe_level() -> None:
    executor = SimulatedSkillExecutor([SimulationRule("observe_area", True)])
    cycle = DeterministicDecisionCycle(executor, AutonomyLevel.OBSERVE)
    result = cycle.run(_state(), Goal.OBSERVE_AREA)
    assert result.blocked is True
    assert result.execution.executed is False
    assert executor.executions == []


def test_invalid_state_never_reaches_executor() -> None:
    state = _state()
    state.apply(DecodedObservation("bad", "player_info", {"entity_id": 1, "hp": 101, "hp_max": 100}, 0.9, "fixture"))
    executor = SimulatedSkillExecutor([SimulationRule("observe_area", True)])
    cycle = DeterministicDecisionCycle(executor, AutonomyLevel.ASSISTED)
    result = cycle.run(state, Goal.OBSERVE_AREA)
    assert result.blocked is True
    assert executor.executions == []
