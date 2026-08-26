from datetime import datetime, timezone

from app.zmsia.core.contracts import Observation
from app.zmsia.core.providers import MockDecisionProvider
from app.zmsia.core.safety import DefaultSafetyPolicy
from app.zmsia.core.safe_evaluation_orchestrator import SafeEvaluatedZMSIAOrchestrator


def _observation() -> Observation:
    """Build a deterministic idle observation for the dry-run cycle tests."""
    return Observation(
        observation_id="obs-1",
        timestamp_ms=int(datetime.now(timezone.utc).timestamp() * 1000),
        source="test",
        data={"state": "idle"},
        confidence=1.0,
    )


def test_full_dry_run_cycle_passes_all_gates_and_records_telemetry():
    """A noop decision must pass validation, safety, evaluation and telemetry."""
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
    assert events[0].action_type == "noop"


def test_disallowed_mock_action_is_blocked_and_telemetry_preserved():
    """A non-noop mock action must be rejected and recorded as unsafe."""
    orchestrator = SafeEvaluatedZMSIAOrchestrator(
        MockDecisionProvider(action_type="move"),
        DefaultSafetyPolicy(),
    )

    result = orchestrator.run_evaluated_once(_observation())

    assert result.safe_cycle.allowed is False
    assert result.accepted is False
    event = orchestrator.telemetry_snapshot()[0]
    assert event.safety_allowed is False
    assert event.evaluation_accepted is False
    assert event.reasons
