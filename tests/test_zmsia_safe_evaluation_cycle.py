from datetime import datetime, timezone

from app.zmsia.core.providers import MockDecisionProvider
from app.zmsia.core.safety import DefaultSafetyPolicy
from app.zmsia.core.safe_evaluation_orchestrator import SafeEvaluatedZMSIAOrchestrator
from app.zmsia.core.contracts import Observation


def _observation() -> Observation:
    return Observation(
        observation_id="obs-1",
        timestamp_ms=int(datetime.now(timezone.utc).timestamp() * 1000),
        source="test",
        data={"state": "idle"},
        confidence=1.0,
    )


def test_full_dry_run_cycle_passes_all_gates_and_records_telemetry():
    orchestrator = SafeEvaluatedZMSIAOrchestrator(
        MockDecisionProvider(),
        DefaultSafetyPolicy(),
    )

    result = orchestrator.run_evaluated_once(_observation())

    assert result.safe_cycle.allowed is True
    assert result.evaluation.accepted is True
    assert result.accepted is True

    events = orchestrator.telemetry_snapshot()
    assert len(events) == 1
    assert events[0].safety_allowed is True
    assert events[0].evaluation_accepted is True
    assert events[0].action_id == "noop"


def test_disallowed_mock_action_is_blocked_and_telemetry_preserved():
    orchestrator = SafeEvaluatedZMSIAOrchestrator(
        MockDecisionProvider(action_id="move"),
        DefaultSafetyPolicy(),
    )

    result = orchestrator.run_evaluated_once(_observation())

    assert result.safe_cycle.allowed is False
    assert result.accepted is False
    event = orchestrator.telemetry_snapshot()[0]
    assert event.safety_allowed is False
    assert event.evaluation_accepted is False
    assert event.reasons
