"""End-to-end candidate validation: sandbox -> replay -> regression."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, Iterable

from .replay import ReplayCase, anti_forgetting_gate
from .replay_runner import ReplayResult
from .sandbox import SandboxBackend, SandboxRequest, SandboxResult


RequestFactory = Callable[[ReplayCase], SandboxRequest]


@dataclass(frozen=True, slots=True)
class CandidateValidationReport:
    sandbox_results: tuple[SandboxResult, ...]
    replay_results: tuple[ReplayResult, ...]
    replay_passed: bool
    anti_forgetting_passed: bool
    regressions: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return (
            bool(self.sandbox_results)
            and all(result.status == "PASS" and result.isolation not in {"", "none", "unverified"} for result in self.sandbox_results)
            and self.replay_passed
            and self.anti_forgetting_passed
        )


class CandidateValidationPipeline:
    """Execute each protected replay case in the injected sandbox backend."""

    def __init__(self, sandbox: SandboxBackend, request_factory: RequestFactory) -> None:
        self.sandbox = sandbox
        self.request_factory = request_factory

    def evaluate(
        self,
        cases: Iterable[ReplayCase],
        baseline_scores: dict[str, float],
        candidate_scores: dict[str, float],
        *,
        tolerance: float = 0.0,
    ) -> CandidateValidationReport:
        sandbox_results: list[SandboxResult] = []
        replay_results: list[ReplayResult] = []
        for case in cases:
            sandbox_result = self.sandbox.execute(self.request_factory(case))
            sandbox_results.append(sandbox_result)
            if sandbox_result.status != "PASS":
                actual = {"sandbox_status": sandbox_result.status, "stderr": sandbox_result.stderr}
            else:
                try:
                    parsed = json.loads(sandbox_result.stdout)
                    actual = parsed if isinstance(parsed, dict) else {"result": parsed}
                except json.JSONDecodeError as exc:
                    actual = {"stdout": sandbox_result.stdout, "parse_error": str(exc)}
            passed = _matches_expected(case.expected, actual)
            detail = "expected output matched" if passed else "expected output mismatch"
            replay_results.append(ReplayResult(case.case_id, passed, case.expected, actual, detail))

        anti_ok, regressions = anti_forgetting_gate(
            baseline_scores, candidate_scores, tolerance=tolerance
        )
        replay_ok = all(result.passed for result in replay_results)
        return CandidateValidationReport(
            tuple(sandbox_results),
            tuple(replay_results),
            replay_ok,
            anti_ok,
            tuple(regressions),
        )


def _matches_expected(expected: dict, actual: dict) -> bool:
    return all(actual.get(key) == value for key, value in expected.items())
