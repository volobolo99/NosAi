from __future__ import annotations

import json
from pathlib import Path

from app.dashboard import ci_evidence


def test_missing_ci_evidence_is_not_run(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "missing.json"
    monkeypatch.setattr(ci_evidence, "EVIDENCE_PATH", path)
    result = ci_evidence.load_ci_evidence()
    assert result["status"] == "NOT_RUN"


def test_ci_evidence_loads_junit_and_coverage_snapshot(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "latest.json"
    path.write_text(
        json.dumps(
            {
                "schema": 2,
                "ci": {"status": "PASS"},
                "junit": {"status": "PASS", "tests": 10, "failures": 0},
                "coverage": {"status": "PASS", "line_percent": 87.5},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(ci_evidence, "EVIDENCE_PATH", path)
    result = ci_evidence.load_ci_evidence()
    assert result["ci"]["status"] == "PASS"
    assert result["junit"]["tests"] == 10
    assert result["coverage"]["line_percent"] == 87.5
    assert result["source"] == str(path)
