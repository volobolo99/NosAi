from datetime import datetime, timezone

from app.zmsia.core.contracts import Action, Decision, Observation
from app.zmsia.core.providers import MockDecisionProvider
from app.zmsia.core.safety import DefaultSafetyPolicy
from app.zmsia.core.safety_orchestrator import SafeZMSIAOrchestrator


def make_observation() -> Observation:
    """Build a deterministic idle observation for safety tests."""
    return Observation(
        observation_id="obs-safe-1",
        timestamp_ms=int(datetime.now(timezone.utc).timestamp() * 1000),
        source="test",
        data={"state": "idle"},
        confidence=1.0,
    )


def test_safe_orchestrator_allows_dry_run_noop():
    """The concrete default policy must allow the noop action type."""
    action = Action(schema_version=1, action_id="a1", action_type="noop", parameters={})
    decision = Decision(
        schema_version=1,
        decision_id="d1",
        goal_id="default",
        action_id="a1",
        action_type="noop",
        parameters={},
        rationale="safe dry-run",
        confidence=1.0,
    )
    result = SafeZMSIAOrchestrator(
        MockDecisionProvider(), DefaultSafetyPolicy()
    ).run_safe_once(make_observation())
    assert result.allowed is True
    assert result.reason == "allowed"
    assert result.cycle.action.action_type == action.action_type


def test_safe_orchestrator_denies_unknown_action():
    """The concrete default policy must deny unknown action types."""
    action = Action(schema_version=1, action_id="a2", action_type="unknown", parameters={})
    decision = Decision(
        schema_version=1,
        decision_id="d2",
        goal_id="default",
        action_id="a2",
        action_type="unknown",
        parameters={},
        rationale="must be denied",
        confidence=1.0,
    )
    assert action.action_type == decision.action_type
    result = SafeZMSIAOrchestrator(
        MockDecisionProvider(action_type="unknown"), DefaultSafetyPolicy()
    ).run_safe_once(make_observation())
    assert result.allowed is False
    assert "action type" in result.reason
