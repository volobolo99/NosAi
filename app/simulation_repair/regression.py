"""Candidate regression evaluation built on protected replay cases."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .replay import ReplayCase, anti_forgetting_gate
from .replay_runner import ReplayResult, ReplayRunner, replay_passed


@dataclass(frozen=True, slots=True)
class RegressionReport:
    replay_results: tuple[ReplayResult, ...]
    replay_passed: bool
    anti_forgetting_passed: bool
    regressions: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return self.replay_passed and self.anti_forgetting_passed


class CandidateRegressionSuite:
    """Run protected replay and score gates for a candidate implementation."""

    def __init__(self, runner: ReplayRunner) -> None:
        self.runner = runner

    def evaluate(
        self,
        cases: Iterable[ReplayCase],
        baseline_scores: dict[str, float],
        candidate_scores: dict[str, float],
        *,
        tolerance: float = 0.0,
    ) -> RegressionReport:
        replay_results = tuple(self.runner.run(cases))
        anti_ok, regressions = anti_forgetting_gate(
            baseline_scores, candidate_scores, tolerance=tolerance
        )
        return RegressionReport(
            replay_results=replay_results,
            replay_passed=replay_passed(replay_results),
            anti_forgetting_passed=anti_ok,
            regressions=tuple(regressions),
        )
