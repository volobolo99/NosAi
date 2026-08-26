from __future__ import annotations

from app.autonomy.planner import Goal
from app.autonomy.replay_scenarios import ReplayObservation, ReplayScenarioExtractor
from app.autonomy.nostale_scenarios import ScenarioKind


def test_replay_window_becomes_golden_fixture() -> None:
    observations = [
        ReplayObservation(2, 2.0, "player_info", {"entity_id": 1, "hp": 80, "hp_max": 100, "mp": 50, "mp_max": 100}),
        ReplayObservation(1, 1.0, "player_info", {"entity_id": 1, "hp": 90, "hp_max": 100, "mp": 60, "mp_max": 100}),
    ]
    scenario = ReplayScenarioExtractor("replay-001").extract(
        observations,
        scenario_id="REAL-001",
        kind=ScenarioKind.HEALTHY_IDLE,
        goal=Goal.OBSERVE_AREA,
    )
    assert scenario.source_replay == "replay-001"
    assert scenario.start_sequence == 1
    assert scenario.end_sequence == 2
    assert scenario.valid is True
    assert scenario.expected_block is False
    assert scenario.state.player.hp == 80


def test_invalid_replay_window_becomes_blocked_golden_fixture() -> None:
    observations = [
        ReplayObservation(1, 1.0, "player_info", {"entity_id": 1, "hp": 101, "hp_max": 100}),
    ]
    scenario = ReplayScenarioExtractor("replay-bad").extract(
        observations,
        scenario_id="REAL-BAD-001",
        kind=ScenarioKind.INVALID_STATE,
        goal=Goal.OBSERVE_AREA,
    )
    assert scenario.valid is False
    assert scenario.expected_block is True
