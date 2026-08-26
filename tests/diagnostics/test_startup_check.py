from __future__ import annotations

import json

from app.diagnostics.startup_check import CheckResult, run_startup_checks
from app.diagnostics.support_bundle import write_support_bundle


def test_startup_report_is_serializable(tmp_path) -> None:
    report = run_startup_checks()
    assert report.schema_version == "nosai-startup-report-v1"
    assert report.checks
    path = write_support_bundle(report, tmp_path / "nosai-diagnostics.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["format"] == "nosai-support-bundle-v1"


def test_failing_extra_check_is_captured(tmp_path) -> None:
    def broken() -> CheckResult:
        raise RuntimeError("fixture failure")

    report = run_startup_checks([("fixture", broken)])
    assert report.ok is False
    assert report.checks[-1].status == "FAIL"
