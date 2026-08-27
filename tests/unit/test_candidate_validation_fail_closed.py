from app.simulation_repair.candidate_validation import CandidateValidationPipeline
from app.simulation_repair.replay import ReplayCase
from app.simulation_repair.sandbox import SandboxResult


class FakeSandbox:
    def execute(self, _request):
        return SandboxResult("NOT_RUN", None, "", "sandbox unavailable", [], "none")


def test_candidate_validation_cannot_pass_when_sandbox_is_not_run():
    case = ReplayCase("case-1", {"x": 1}, {"x": 1})
    pipeline = CandidateValidationPipeline(FakeSandbox(), lambda _case: None)
    report = pipeline.evaluate([case], {"baseline": 1.0}, {"baseline": 1.0})
    assert report.replay_passed is False
    assert report.passed is False
