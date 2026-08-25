from pathlib import Path

from app.pilot import PilotMode, PilotSessionConfig, TestPilot
from app.pilot.adapters import SimulatedClientAdapter


def test_simulation_collects_decisions_without_live_execution(tmp_path: Path) -> None:
    adapter = SimulatedClientAdapter()
    pilot = TestPilot(
        adapter,
        PilotSessionConfig(mode=PilotMode.SIMULATION, ticks=5, telemetry_path=str(tmp_path / "pilot.jsonl")),
    )

    result = pilot.run()

    assert result.ticks == 5
    assert result.decisions == 5
    assert result.valid_decisions == 5
    assert result.ready_for_live_action is False
    assert result.missing_capabilities == ()
    assert (tmp_path / "pilot.jsonl").exists()
    assert adapter.connected is True


def test_missing_capability_is_recorded(tmp_path: Path) -> None:
    adapter = SimulatedClientAdapter(scenario="stale_state")
    pilot = TestPilot(
        adapter,
        PilotSessionConfig(ticks=2, telemetry_path=str(tmp_path / "pilot.jsonl")),
    )

    result = pilot.run()

    assert "player.position" in result.missing_capabilities
    assert "entities" in result.missing_capabilities
    assert any(error.error_id == "P001" for error in result.errors)


def test_unknown_scenario_becomes_runtime_diagnostic(tmp_path: Path) -> None:
    adapter = SimulatedClientAdapter(scenario="unknown")
    pilot = TestPilot(
        adapter,
        PilotSessionConfig(ticks=1, telemetry_path=str(tmp_path / "pilot.jsonl")),
    )

    result = pilot.run()

    assert result.decisions == 0
    assert any(error.error_id == "C004" for error in result.errors)
