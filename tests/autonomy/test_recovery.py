from __future__ import annotations

from app.autonomy.planner import CandidateSkill, DecisionTrace, Goal
from app.autonomy.recovery import RecoveryAction, RecoveryManager


def _trace(valid: bool = True) -> DecisionTrace:
    return DecisionTrace(
        "trace", Goal.OBSERVE_AREA, 1, valid,
        (
            CandidateSkill("observe_area", 0.8, "primary", True),
            CandidateSkill("maintain_state", 0.5, "fallback", True),
        ),
        "observe_area" if valid else None,
        "reason",
    )


def test_failed_execution_retries_within_budget() -> None:
    decision = RecoveryManager(max_retries=1).decide(_trace(), attempt=0, outcome="execution_failed")
    assert decision.action == RecoveryAction.RETRY
    assert decision.skill == "observe_area"
    assert decision.attempt == 1


def test_failed_retry_selects_safe_alternative() -> None:
    decision = RecoveryManager(max_retries=1).decide(_trace(), attempt=1, outcome="execution_failed")
    assert decision.action == RecoveryAction.ALTERNATIVE
    assert decision.skill == "maintain_state"


def test_blocked_execution_uses_safe_fallback() -> None:
    decision = RecoveryManager().decide(_trace(), attempt=0, outcome="execution_blocked")
    assert decision.action == RecoveryAction.SAFE_FALLBACK
    assert decision.skill == "maintain_state"


def test_invalid_state_aborts() -> None:
    decision = RecoveryManager().decide(_trace(False), attempt=0, outcome="execution_failed")
    assert decision.action == RecoveryAction.ABORT
    assert decision.skill is None
