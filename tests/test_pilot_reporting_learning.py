from pathlib import Path

from app.pilot.cycle import run_cycle
from app.pilot.learning import update_learning_ledger
from app.pilot.models import PilotError
from app.pilot.reporting import write_html_report, write_json_report


def test_learning_ledger_accumulates_repeated_errors(tmp_path: Path) -> None:
    errors = [{"error_id": "P001", "category": "perception", "message": "missing state"}]
    ledger = tmp_path / "learning.json"
    update_learning_ledger(errors, "stale_state", ledger)
    records = update_learning_ledger(errors, "stale_state", ledger)
    assert records[0].error_id == "P001"
    assert records[0].observed_count == 2


def test_reports_are_written(tmp_path: Path) -> None:
    from app.pilot.adapters import SimulatedClientAdapter
    from app.pilot.models import PilotMode, PilotSessionConfig
    from app.pilot.runner import TestPilot

    result = TestPilot(
        SimulatedClientAdapter("combat_basic"),
        PilotSessionConfig(mode=PilotMode.SIMULATION, ticks=3, telemetry_path=str(tmp_path / "x.jsonl")),
    ).run()
    assert write_json_report(result, tmp_path / "r.json").exists()
    assert write_html_report(result, tmp_path / "r.html").exists()


def test_full_cycle_is_safe_and_persistent(tmp_path: Path) -> None:
    result = run_cycle(scenarios=("combat_basic", "stale_state"), ticks=3, output_dir=tmp_path)
    assert result["ready_for_live_action"] is False
    assert Path(result["learning_ledger"]).exists()
    assert Path(result["repair_queue"]).exists()
    assert (tmp_path / "combat_basic.report.json").exists()
    assert (tmp_path / "stale_state.report.html").exists()
