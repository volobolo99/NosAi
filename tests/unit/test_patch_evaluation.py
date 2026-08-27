from app.simulation_repair.patch_evaluation import evaluate_patch
from app.simulation_repair.sandbox import SandboxResult


def sandbox(status="PASS", isolation="isolated"):
    return SandboxResult(status, 0 if status == "PASS" else 1, "", "", [], isolation)


def test_patch_requires_all_gates():
    result = evaluate_patch("c1", sandbox(), replay_passed=True, regression_passed=False, anti_forgetting_passed=True)
    assert result.status == "FAIL"


def test_patch_passes_only_with_complete_evidence():
    result = evaluate_patch("c1", sandbox(), replay_passed=True, regression_passed=True, anti_forgetting_passed=True)
    assert result.status == "PASS"


def test_patch_cannot_pass_without_sandbox_execution():
    result = evaluate_patch("c1", sandbox("NOT_RUN"), replay_passed=True, regression_passed=True, anti_forgetting_passed=True)
    assert result.status == "FAIL"


def test_patch_cannot_pass_without_verified_isolation():
    result = evaluate_patch("c1", sandbox(isolation="none"), replay_passed=True, regression_passed=True, anti_forgetting_passed=True)
    assert result.status == "FAIL"
    assert "verified isolation" in result.detail


def test_patch_passes_with_verified_windows_sandbox():
    result = evaluate_patch(
        "c1",
        sandbox(isolation="windows-sandbox"),
        replay_passed=True,
        regression_passed=True,
        anti_forgetting_passed=True,
    )
    assert result.status == "PASS"
