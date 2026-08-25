import json
from pathlib import Path

from app.pilot import PilotMode
from app.pilot.models import PilotResult
from app.pilot.reporting import result_to_dict, write_html_report, write_json_report


def make_result() -> PilotResult:
    return PilotResult(
        session_id="test-session",
        mode=PilotMode.SIMULATION,
        ticks=1,
        decisions=1,
        valid_decisions=1,
        blocked_decisions=0,
        state_quality_counts={"valid": 1, "degraded": 0, "unusable": 0},
        errors=(),
        missing_capabilities=(),
        avg_decision_latency_ms=0.1,
    )


def test_result_to_dict_includes_computed_live_safety_gate() -> None:
    result = make_result()

    data = result_to_dict(result)

    assert data["ready_for_live_action"] is False


def test_reports_write_with_computed_live_safety_gate(tmp_path: Path) -> None:
    result = make_result()
    json_path = write_json_report(result, tmp_path / "report.json")
    html_path = write_html_report(result, tmp_path / "report.html")

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")

    assert payload["ready_for_live_action"] is False
    assert "ready_for_live_action" in html
    assert "False" in html
