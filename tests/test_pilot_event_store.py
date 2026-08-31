from app.pilot.event_store import PilotEventStore
from app.pilot.telemetry_schema import PilotEventType, SCHEMA_VERSION


def test_event_store_writes_versioned_jsonl(tmp_path) -> None:
    store = PilotEventStore(tmp_path / "events.jsonl")
    store.record(
        PilotEventType.STATE_OBSERVED,
        "session-1",
        tick=3,
        state_quality="valid",
        payload={"entities": 1},
    )

    records = store.read_all()
    assert len(records) == 1
    assert records[0]["schema_version"] == SCHEMA_VERSION
    assert records[0]["event_type"] == PilotEventType.STATE_OBSERVED.value
    assert records[0]["payload"] == {"entities": 1}
