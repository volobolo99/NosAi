"""End-to-end candidate validation: sandbox -> replay -> regression -> evidence."""
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
        sandbox_ok = bool(self.sandbox_results) and all(
            result.status == "PASS"
            and result.isolation not in {"", "none", "unverified"}
            for result in self.sandbox_results
        )
        return sandbox_ok and self.replay_passed and self.anti_forgetting_passed


class CandidateValidationPipeline:
    """Execute protected cases in isolation and evaluate regression gates."""

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
            actual = self._actual_from_sandbox(sandbox_result)
            passed = sandbox_result.status == "PASS" and _matches_expected(case.expected, actual)
            detail = "expected output matched" if passed else "sandbox execution or expected output failed"
            replay_results.append(ReplayResult(case.case_id, passed, case.expected, actual, detail))

        anti_ok, regressions = anti_forgetting_gate(
            baseline_scores, candidate_scores, tolerance=tolerance
        )
        return CandidateValidationReport(
            tuple(sandbox_results),
            tuple(replay_results),
            all(result.passed for result in replay_results),
            anti_ok,
            tuple(regressions),
        )

    @staticmethod
    def _actual_from_sandbox(result: SandboxResult) -> dict:
        if result.status != "PASS":
            return {"sandbox_status": result.status, "stderr": result.stderr}
        try:
            parsed = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            return {"stdout": result.stdout, "parse_error": str(exc)}
        return parsed if isinstance(parsed, dict) else {"result": parsed}


def _matches_expected(expected: dict, actual: dict) -> bool:
    return all(actual.get(key) == value for key, value in expected.items())
