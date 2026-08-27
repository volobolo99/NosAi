from nosai.runtime.nostale_observer import NosTaleLiveObserver


def test_live_observer_is_read_only_and_collects_external_observations():
    observer = NosTaleLiveObserver(max_observations=2)
    assert observer.execution_enabled is False
    assert "read_only" in observer.capabilities
    observer.ingest({"map": "1", "hp": "100", "mp": "50"})
    latest = observer.latest()
    assert latest is not None
    assert latest.state["map"] == "1"


def test_observer_is_bounded():
    observer = NosTaleLiveObserver(max_observations=2)
    observer.ingest({"n": "1"})
    observer.ingest({"n": "2"})
    observer.ingest({"n": "3"})
    assert [item.state["n"] for item in observer.observations()] == ["2", "3"]
