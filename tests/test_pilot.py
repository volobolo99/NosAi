from pathlib import Path

from app.pilot import PilotMode, PilotSessionConfig, TestPilot as PilotRunner
from app.pilot.adapters import SimulatedClientAdapter


def test_simulation_collects_decisions_without_live_execution(tmp_path: Path) -> None:
    """Verify simulation produces validated decisions without live execution."""
    adapter = SimulatedClientAdapter()
    pilot = PilotRunner(
        adapter,
        PilotSessionConfig(mode=PilotMode.SIMULATION, ticks=5, telemetry_path=str(tmp_path / "pilot.jsonl")),
    )

    result = pilot.run()

    assert result.ticks == 5
    assert result.decisions == 5
    assert result.valid_decisions == 5
    assert result.blocked_decisions == 0
    assert result.state_quality_counts["valid"] == 5
    assert result.ready_for_live_action is False
    assert result.missing_capabilities == ()
    assert (tmp_path / "pilot.jsonl").exists()
    assert adapter.connected is True


def test_missing_capability_blocks_decision(tmp_path: Path) -> None:
    """Verify unsafe missing capabilities prevent the decision stage."""
    adapter = SimulatedClientAdapter(scenario="stale_state")
    pilot = PilotRunner(
        adapter,
        PilotSessionConfig(ticks=2, telemetry_path=str(tmp_path / "pilot.jsonl")),
    )

    result = pilot.run()

    assert result.decisions == 0
    assert result.valid_decisions == 0
    assert result.blocked_decisions == 2
    assert result.state_quality_counts["unusable"] == 2
    assert "player.position" in result.missing_capabilities
    assert "entities" in result.missing_capabilities
    assert any(error.error_id == "P001" for error in result.errors)
    assert all(error.metadata["state_quality"] == "unusable" for error in result.errors)


def test_unknown_scenario_becomes_runtime_diagnostic(tmp_path: Path) -> None:
    """Verify an unsupported simulation scenario becomes a runtime diagnostic."""
    adapter = SimulatedClientAdapter(scenario="unknown")
    pilot = PilotRunner(
        adapter,
        PilotSessionConfig(ticks=1, telemetry_path=str(tmp_path / "pilot.jsonl")),
    )

    result = pilot.run()

    assert result.decisions == 0
    assert any(error.error_id == "C004" for error in result.errors)
