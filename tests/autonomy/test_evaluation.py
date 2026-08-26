from __future__ import annotations

from app.autonomy.evaluation import EvaluationLedger
from app.nostale_perception.autonomy import ExecutionResult


def test_success_is_recorded_in_skill_ledger() -> None:
    ledger = EvaluationLedger()
    evidence = ledger.evaluate("trace-1", "observe_area", ExecutionResult("observe_area", True, True, True, "ok"))
    assert evidence.outcome == "success"
    assert evidence.evaluation.score == 1.0
    assert ledger.skill_ledger.skills["observe_area"].attempts == 1
    assert ledger.skill_ledger.skills["observe_area"].successes == 1


def test_failure_is_recorded_without_false_verification() -> None:
    ledger = EvaluationLedger()
    evidence = ledger.evaluate("trace-2", "observe_area", ExecutionResult("observe_area", True, True, False, "failed"))
    assert evidence.outcome == "failure"
    record = ledger.skill_ledger.skills["observe_area"]
    assert record.failures == 1
    assert record.verified is False


def test_blocked_execution_does_not_count_as_success() -> None:
    ledger = EvaluationLedger()
    evidence = ledger.evaluate("trace-3", "observe_area", ExecutionResult("observe_area", False, False, None, "blocked"))
    assert evidence.outcome == "blocked"
    assert ledger.success_rate() == 0.0
