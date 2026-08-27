import pytest

from nosai.runtime.telemetry import TelemetryCollector


def test_telemetry_is_bounded_and_ordered():
    collector = TelemetryCollector(max_events=2)
    collector.record("s1", "simulation", "move", "accepted")
    collector.record("s1", "simulation", "attack", "accepted")
    collector.record("s1", "simulation", "stop", "accepted")
    events = collector.events()
    assert [e.sequence for e in events] == [2, 3]
    assert [e.action for e in events] == ["attack", "stop"]


def test_telemetry_rejects_invalid_identity_fields():
    collector = TelemetryCollector()
    with pytest.raises(ValueError):
        collector.record("", "simulation", "move", "accepted")
    with pytest.raises(ValueError):
        collector.record("s1", "", "move", "accepted")


def test_telemetry_counts_do_not_authorize_anything():
    collector = TelemetryCollector()
    collector.record("s1", "simulation", "move", "accepted")
    collector.record("s1", "error", "move", "timeout")
    assert collector.counts() == {"simulation": 1, "error": 1}
