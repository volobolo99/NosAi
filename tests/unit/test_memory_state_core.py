from app.memory import MemoryItem, MemoryScope, MemoryStore, MemoryType, StateRecord, StateStore


def test_memory_roundtrip_normalizes_provenance(tmp_path):
    store = MemoryStore(tmp_path / "memory.json")
    item = MemoryItem("m1", MemoryType.EPISODIC, MemoryScope.SESSION, "event", "2026-08-27T00:00:00Z", "2026-08-27T00:00:00Z", provenance=("source",))
    store.put(item)
    loaded = store.get("m1")
    assert loaded == item
    assert isinstance(loaded.provenance, tuple)


def test_state_is_monotonic(tmp_path):
    store = StateStore(tmp_path / "state.json")
    store.save(StateRecord("run-1", "running", 2, "2026-08-27T00:00:00Z", {"step": 2}))
    store.save(StateRecord("run-1", "done", 3, "2026-08-27T00:01:00Z", {"step": 3}))
    assert store.load("run-1").version == 3

    try:
        store.save(StateRecord("run-1", "stale", 2, "2026-08-27T00:02:00Z"))
    except ValueError:
        pass
    else:
        raise AssertionError("state version regression must fail closed")
