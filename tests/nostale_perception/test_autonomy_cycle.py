from __future__ import annotations

from app.nostale_perception.autonomy import SkillRequest
from app.nostale_perception.autonomy_cycle import run_simulated_cycle
from app.nostale_perception.game_state import GameState
from app.nostale_perception.simulated_executor import SimulatedSkillExecutor, SimulationRule
from app.nostale_perception.skill_ledger import SkillLedger, SkillRecord


def test_first_simulated_autonomy_cycle_is_end_to_end() -> None:
    ledger = SkillLedger()
    ledger.upsert(SkillRecord("observe_area", "1"))
    executor = SimulatedSkillExecutor([SimulationRule("observe_area", True)])

    result = run_simulated_cycle(
        GameState.empty(),
        SkillRequest("observe_area", 0.9, "simulation"),
        executor,
        ledger,
    )

    assert result.accepted is True
    assert result.executed is True
    assert result.success is True
    assert result.ledger_success_rate == 1.0
    assert result.verified is False


def test_simulation_never_touches_real_executor_boundary() -> None:
    executor = SimulatedSkillExecutor()
    result = executor.execute(SkillRequest("missing", 1.0, "test"), GameState.empty())
    assert result.executed is False
    assert executor.executions == []
