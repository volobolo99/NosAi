from datetime import datetime, timezone

import pytest

from nosai.data.live_dataset import LiveDatasetRecorder


def test_recorder_normalizes_timestamp_and_reports_quality():
    recorder = LiveDatasetRecorder(max_records=2)
    timestamp = datetime(2026, 8, 27, 15, 0, tzinfo=timezone.utc)
    first = recorder.append("s-15", {"map": "sandbox", "hp": 100}, observed_at=timestamp)
    second = recorder.append("s-15", {"map": "sandbox", "hp": 99}, observed_at=timestamp)
    assert first.session_id == "s-15"
    assert first.observed_at.endswith("+00:00")
    assert recorder.quality() == {"records": 2, "sessions": 1}
    assert second.record_id != first.record_id


def test_recorder_is_bounded():
    recorder = LiveDatasetRecorder(max_records=2)
    recorder.append("s-15", {"n": 1})
    recorder.append("s-15", {"n": 2})
    recorder.append("s-15", {"n": 3})
    assert [r.payload["n"] for r in recorder.records()] == [2, 3]


def test_recorder_rejects_invalid_input():
    recorder = LiveDatasetRecorder()
    with pytest.raises(ValueError):
        recorder.append("", {"hp": 1})
    with pytest.raises(ValueError):
        recorder.append("s", {})
    with pytest.raises(ValueError):
        recorder.append("s", {"hp": 1}, observed_at=datetime(2026, 8, 27, 15, 0))
