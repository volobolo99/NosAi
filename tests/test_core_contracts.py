from datetime import datetime, timezone

import pytest

from app.core.contracts import (
    CandidateAction,
    DecisionStatus,
    Evidence,
    Goal,
    Risk,
    WorldState,
    noop_decision,
)


def test_world_state_requires_valid_confidence() -> None:
    state = WorldState(
        state_id="s1",
        observed_at=datetime.now(timezone.utc),
        confidence=0.75,
    )
    assert state.confidence == 0.75

    with pytest.raises(ValueError):
        WorldState(
            state_id="s2",
            observed_at=datetime.now(timezone.utc),
            confidence=1.1,
        )


def test_evidence_requires_source_and_valid_confidence() -> None:
    evidence = Evidence(source="replay", confidence=0.9)
    assert evidence.source == "replay"

    with pytest.raises(ValueError):
        Evidence(source="", confidence=1.0)


def test_candidate_action_carries_risk_and_preconditions() -> None:
    action = CandidateAction(
        action_id="a1",
        action_type="noop",
        risk=Risk(score=0.0, category="none"),
        preconditions=("safe_mode",),
    )
    assert action.risk.score == 0.0
    assert action.preconditions == ("safe_mode",)


def test_noop_is_deterministic_and_has_no_action() -> None:
    first = noop_decision()
    second = noop_decision()

    assert first.status is DecisionStatus.NOOP
    assert first.action is None
    assert first.provider == "deterministic-noop"
    assert first == second


def test_goal_requires_identity_and_objective() -> None:
    goal = Goal(goal_id="g1", objective="observe")
    assert goal.objective == "observe"

    with pytest.raises(ValueError):
        Goal(goal_id="", objective="observe")
