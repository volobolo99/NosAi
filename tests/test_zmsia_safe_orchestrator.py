from datetime import datetime, timezone

from app.zmsia.core.contracts import Action, Decision, Observation
from app.zmsia.core.providers import MockDecisionProvider
from app.zmsia.core.safety import SafetyPolicy
from app.zmsia.core.safety_orchestrator import SafeZMSIAOrchestrator


def make_observation() -> Observation:
    return Observation(
        schema_version="1",
        observation_id="obs-safe-1",
        timestamp=datetime.now(timezone.utc),
        source="test",
        payload={"state": "idle"},
        confidence=1.0,
    )


def test_safe_orchestrator_allows_dry_run_noop():
    action = Action(schema_version="1", action_id="a1", action_type="noop", parameters={})
    decision = Decision(
        schema_version="1",
        decision_id="d1",
        action=action,
        rationale="safe dry-run",
        confidence=1.0,
    )
    result = SafeZMSIAOrchestrator(
        MockDecisionProvider(decision), SafetyPolicy(allowed_actions={"noop"})
    ).run_safe_once(make_observation())
    assert result.allowed is True
    assert result.reason == "allowed"


def test_safe_orchestrator_denies_unknown_action():
    action = Action(schema_version="1", action_id="a2", action_type="unknown", parameters={})
    decision = Decision(
        schema_version="1",
        decision_id="d2",
        action=action,
        rationale="must be denied",
        confidence=1.0,
    )
    result = SafeZMSIAOrchestrator(
        MockDecisionProvider(decision), SafetyPolicy(allowed_actions={"noop"})
    ).run_safe_once(make_observation())
    assert result.allowed is False
    assert "not allowed" in result.reason
