from datetime import datetime, timezone

from app.zmsia.core.contracts import Action, Decision, State
from app.zmsia.core.evaluation_gate import DeterministicEvaluationGate
from app.zmsia.core.telemetry import CycleTelemetry, InMemoryTelemetry


def _state() -> State:
    return State(
        schema_version="1",
        state_id="state-1",
        timestamp=datetime.now(timezone.utc),
        values={},
        confidence=1.0,
    )


def _decision(action: Action) -> Decision:
    return Decision(
        schema_version="1",
        decision_id="decision-1",
        action=action,
        rationale="test",
        confidence=1.0,
    )


def test_evaluation_accepts_dry_run_noop():
    action = Action(schema_version="1", action_id="action-1", action_type="noop", parameters={})
    result = DeterministicEvaluationGate().evaluate(_state(), _decision(action), action)
    assert result.accepted is True


def test_evaluation_rejects_non_noop_action():
    action = Action(schema_version="1", action_id="action-1", action_type="move", parameters={})
    result = DeterministicEvaluationGate().evaluate(_state(), _decision(action), action)
    assert result.accepted is False
    assert "action_not_allowed_in_dry_run" in result.reasons


def test_telemetry_is_append_only_snapshot():
    telemetry = InMemoryTelemetry()
    telemetry.record(
        CycleTelemetry(
            cycle_id="cycle-1",
            timestamp=telemetry.now(),
            observation_id="obs-1",
            decision_id="decision-1",
            action_type="noop",
            safety_allowed=True,
        )
    )
    snapshot = telemetry.snapshot()
    assert len(snapshot) == 1
    assert snapshot[0].cycle_id == "cycle-1"
