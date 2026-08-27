from __future__ import annotations

from app.simulation_repair.candidate_validation import CandidateValidationPipeline
from app.simulation_repair.replay import ReplayCase
from app.simulation_repair.sandbox import SandboxRequest, SandboxResult


class FakeSandbox:
    def execute(self, request: SandboxRequest) -> SandboxResult:
        return SandboxResult(
            status="PASS",
            exit_code=0,
            stdout='{"result": 4}',
            stderr="",
            evidence=["stdout.txt"],
            isolation="fake-isolated",
        )


def test_candidate_validation_connects_sandbox_replay_and_anti_forgetting():
    case = ReplayCase("case-1", {"x": 2}, {"result": 4})
    pipeline = CandidateValidationPipeline(
        FakeSandbox(),
        lambda replay_case: SandboxRequest(
            candidate_id="candidate-1",
            files={"scenario.json": "{}"},
            command=["cmd.exe", "/d", "/c", "echo"],
        ),
    )
    report = pipeline.evaluate(
        [case],
        baseline_scores={"case-1": 1.0},
        candidate_scores={"case-1": 1.0, "new": 1.1},
    )
    assert report.passed is True
    assert report.replay_passed is True
    assert report.anti_forgetting_passed is True


def test_candidate_validation_blocks_sandbox_failure():
    class FailingSandbox:
        def execute(self, request):
            return SandboxResult("NOT_RUN", None, "", "sandbox unavailable", [], "none")

    case = ReplayCase("case-1", {}, {})
    pipeline = CandidateValidationPipeline(
        FailingSandbox(),
        lambda replay_case: SandboxRequest(candidate_id="candidate-1", command=["cmd.exe"]),
    )
    report = pipeline.evaluate([case], {"case-1": 1.0}, {"case-1": 1.0})
    assert report.passed is False
    assert report.replay_passed is False
