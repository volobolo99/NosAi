from app.self_repair.telemetry import TelemetryStore


def test_telemetry_records_first_and_completed_cycle(tmp_path):
    store = TelemetryStore(tmp_path / "telemetry.jsonl")
    cycle_id = store.start_cycle("startup", {"mode": "sandbox"})
    store.finish_cycle(
        cycle_id,
        "startup",
        "PASS",
        duration_ms=12.5,
        metrics={"tests": 4, "latency_ms": 3.2},
        error_ids=("E-001",),
    )

    records = store.read_all()
    assert len(records) == 2
    assert records[0]["status"] == "STARTED"
    assert records[1]["cycle_id"] == cycle_id
    assert records[1]["metrics"]["tests"] == 4

    summary = store.summary()
    assert summary["records"] == 2
    assert summary["completed"] == 1
    assert summary["statuses"] == {"PASS": 1}
    assert summary["unique_error_ids"] == ["E-001"]


def test_missing_telemetry_file_is_empty(tmp_path):
    store = TelemetryStore(tmp_path / "missing.jsonl")
    assert store.read_all() == []
    assert store.summary() == {
        "records": 0,
        "completed": 0,
        "statuses": {},
        "unique_error_ids": [],
    }
