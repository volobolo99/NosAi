from __future__ import annotations

import json
from pathlib import Path

from app.nostale_perception.evaluation import PerceptionEvaluation
from app.nostale_perception.evaluation_report import QualityGate, gate_evaluation, write_report
from app.nostale_perception.metrics import NumericMetric


def _metric(mae: float | None) -> NumericMetric:
    return NumericMetric(1 if mae is not None else 0, mae, mae, 1.0 if mae is not None else None)


def test_quality_gate_passes_clean_result() -> None:
    result = PerceptionEvaluation(_metric(1), _metric(1), _metric(0.5), _metric(0.5), 1.0)
    assert gate_evaluation(result, QualityGate())[0] is True


def test_quality_gate_reports_failed_metrics() -> None:
    result = PerceptionEvaluation(_metric(10), _metric(1), _metric(0.5), _metric(0.5), 0.8)
    passed, failures = gate_evaluation(result, QualityGate())
    assert not passed
    assert "hp_mae" in failures
    assert "map_accuracy" in failures


def test_report_is_machine_readable(tmp_path: Path) -> None:
    result = PerceptionEvaluation(_metric(1), _metric(1), _metric(0.5), _metric(0.5), 1.0)
    path = tmp_path / "report.json"
    assert write_report(path, result, QualityGate())
    assert json.loads(path.read_text(encoding="utf-8"))["passed"] is True
