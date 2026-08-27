from __future__ import annotations

from app.simulation_repair.regression import CandidateRegressionSuite
from app.simulation_repair.replay import ReplayCase
from app.simulation_repair.replay_runner import ReplayRunner


def test_replay_runner_is_deterministic_and_reports_mismatch():
    cases = [
        ReplayCase("ok", {"x": 2}, {"result": 4}),
        ReplayCase("bad", {"x": 3}, {"result": 8}),
    ]
    runner = ReplayRunner(lambda scenario: {"result": scenario["x"] ** 2})
    results = runner.run(cases)
    assert results[0].passed is True
    assert results[1].passed is False


def test_regression_suite_blocks_anti_forgetting_regression():
    case = ReplayCase("protected", {"x": 2}, {"result": 4})
    runner = ReplayRunner(lambda scenario: {"result": scenario["x"] ** 2})
    report = CandidateRegressionSuite(runner).evaluate(
        [case],
        baseline_scores={"protected": 1.0},
        candidate_scores={"protected": 0.9},
    )
    assert report.replay_passed is True
    assert report.anti_forgetting_passed is False
    assert report.passed is False
    assert report.regressions == ("protected",)


def test_regression_suite_allows_non_regressing_candidate():
    case = ReplayCase("protected", {"x": 2}, {"result": 4})
    runner = ReplayRunner(lambda scenario: {"result": scenario["x"] ** 2})
    report = CandidateRegressionSuite(runner).evaluate(
        [case],
        baseline_scores={"protected": 1.0},
        candidate_scores={"protected": 1.0, "new_capability": 1.2},
    )
    assert report.passed is True
