from datetime import datetime, timezone

from app.zmsia.core.orchestrator import ZMSIAOrchestrator
from app.zmsia.core.providers import MockDecisionProvider
from app.zmsia.core.contracts import Action, Decision, Observation


def test_mock_orchestrator_completes_safe_decision_cycle():
    action = Action(
        schema_version="1",
        action_id="action-1",
        action_type="noop",
        parameters={},
    )
    decision = Decision(
        schema_version="1",
        decision_id="decision-1",
        action=action,
        rationale="deterministic test decision",
        confidence=1.0,
    )
    provider = MockDecisionProvider(decision)
    orchestrator = ZMSIAOrchestrator(provider)

    observation = Observation(
        schema_version="1",
        observation_id="obs-1",
        timestamp=datetime.now(timezone.utc),
        source="test",
        payload={"state": "idle"},
        confidence=1.0,
    )

    result = orchestrator.run_once(observation)

    assert result.observation.observation_id == "obs-1"
    assert result.state.values["observation_id"] == "obs-1"
    assert result.decision.decision_id == "decision-1"
    assert result.action.action_type == "noop"
