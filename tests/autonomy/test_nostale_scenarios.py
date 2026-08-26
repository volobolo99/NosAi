from __future__ import annotations

from app.autonomy.nostale_scenarios import ScenarioKind, all_scenarios
from app.nostale_perception.state_invariants import validate_game_state


def test_scenario_suite_has_expected_coverage() -> None:
    scenarios = all_scenarios()
    kinds = {scenario.kind for scenario in scenarios}
    assert ScenarioKind.HEALTHY_IDLE in kinds
    assert ScenarioKind.LOW_HP in kinds
    assert ScenarioKind.INVALID_STATE in kinds
    assert ScenarioKind.WORLD_ENTITY in kinds
    assert len({scenario.scenario_id for scenario in scenarios}) == len(scenarios)


def test_scenarios_are_built_through_gamestate_boundary() -> None:
    scenarios = all_scenarios()
    invalid = [scenario for scenario in scenarios if scenario.kind == ScenarioKind.INVALID_STATE]
    valid = [scenario for scenario in scenarios if scenario.kind != ScenarioKind.INVALID_STATE]
    assert invalid
    assert any(not validate_game_state(scenario.build()).valid for scenario in invalid)
    assert all(validate_game_state(scenario.build()).valid for scenario in valid)
