from __future__ import annotations

from app.autonomy.golden_dataset import build_dataset, coverage, fingerprint_scenario, to_fixture
from app.autonomy.planner import Goal
from app.autonomy.replay_scenarios import ReplayObservation, ReplayScenarioExtractor
from app.autonomy.nostale_scenarios import ScenarioKind


def _scenario(scenario_id: str):
    return ReplayScenarioExtractor("replay-14").extract(
        [ReplayObservation(1, 1.0, "player_info", {"entity_id": 1, "hp": 80, "hp_max": 100, "mp": 60, "mp_max": 100})],
        scenario_id=scenario_id,
        kind=ScenarioKind.HEALTHY_IDLE,
        goal=Goal.OBSERVE_AREA,
    )


def test_fixture_has_schema_version_and_sha256_fingerprint() -> None:
    fixture = to_fixture(_scenario("GD-001"), "2026.08.14")
    assert fixture.schema_version == "1.0"
    assert len(fixture.fingerprint) == 64


def test_dataset_rejects_duplicate_ids_and_fingerprints() -> None:
    scenario = _scenario("GD-002")
    try:
        build_dataset([scenario, scenario], "2026.08.14")
    except ValueError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("duplicate dataset entries must be rejected")


def test_coverage_is_deterministic() -> None:
    fixtures = build_dataset([_scenario("GD-003")], "2026.08.14")
    assert coverage(fixtures) == {"total": 1, "valid": 1, "invalid": 0, "expected_block": 0}
