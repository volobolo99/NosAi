import pytest

from nosai.data.replay import DatasetReplay


def test_replay_is_deterministic():
    replay = DatasetReplay()
    records = [{"hp": 100}, {"hp": 90}]
    first = replay.replay("s-18", records)
    second = replay.replay("s-18", records)
    assert first == second
    assert first.records == 2


def test_quality_report_counts_invalid_records():
    report = DatasetReplay().quality_report([{"hp": 1}, {}, "bad"])
    assert report == {"total": 3, "valid": 1, "invalid": 2}


def test_replay_rejects_empty_inputs():
    with pytest.raises(ValueError):
        DatasetReplay().replay("s-18", [])
    with pytest.raises(ValueError):
        DatasetReplay().replay("", [{"hp": 1}])
