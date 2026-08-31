from app.pilot.telemetry_schema import (
    SCHEMA_VERSION,
    PilotEventType,
    PilotTelemetryEvent,
    validate_event,
)


def test_event_round_trip_shape() -> None:
    event = PilotTelemetryEvent(
        event_type=PilotEventType.DECISION_BLOCKED,
        session_id="session-1",
        event_id="event-1",
        tick=7,
        state_quality="unusable",
        payload={"missing_capabilities": ["target"]},
    )

    validate_event(event)
    data = event.to_dict()

    assert data["schema_version"] == SCHEMA_VERSION
    assert data["event_type"] == "decision_blocked"
    assert data["session_id"] == "session-1"
    assert data["tick"] == 7
    assert data["payload"]["missing_capabilities"] == ["target"]


def test_rejects_invalid_quality() -> None:
    event = PilotTelemetryEvent(
        event_type=PilotEventType.STATE_OBSERVED,
        session_id="session-1",
        event_id="event-1",
        state_quality="broken",
    )

    try:
        validate_event(event)
    except ValueError as exc:
        assert "invalid state_quality" in str(exc)
    else:
        raise AssertionError("invalid state quality was accepted")


def test_rejects_negative_tick() -> None:
    event = PilotTelemetryEvent(
        event_type=PilotEventType.STATE_OBSERVED,
        session_id="session-1",
        event_id="event-1",
        tick=-1,
    )

    try:
        validate_event(event)
    except ValueError as exc:
        assert "non-negative" in str(exc)
    else:
        raise AssertionError("negative tick was accepted")
