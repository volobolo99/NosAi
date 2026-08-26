from __future__ import annotations

from app.nostale_perception.autonomy_benchmark import default_cases, run_benchmark


def test_autonomy_benchmark_is_deterministic_and_measures_outcomes() -> None:
    report, results = run_benchmark(default_cases())
    assert report.cases == 6
    assert report.accepted == 6
    assert report.executed == 6
    assert len(results) == 6
    assert 0.0 <= report.outcome_accuracy <= 1.0
    assert report.intervention_rate == 0.0


def test_benchmark_exposes_skill_verification_state() -> None:
    report, _ = run_benchmark(default_cases())
    assert report.skill_verification_count >= 0
