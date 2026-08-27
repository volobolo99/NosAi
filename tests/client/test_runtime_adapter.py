import pytest

from app.client import ClientState
from app.client.runtime_adapter import AdapterMode, RuntimeAdapter, RuntimeObservation


def test_mock_mode_is_offline_and_normalized():
    obs = RuntimeAdapter(AdapterMode.MOCK).observe()
    assert obs.source == "mock"
    assert obs.payload["observation_only"] is True


def test_replay_mode_returns_ordered_observations():
    rows = [RuntimeObservation(1, {"hp": 10}, "replay")]
    adapter = RuntimeAdapter("replay", replay=rows)
    assert adapter.observe().payload == {"hp": 10}
    with pytest.raises(RuntimeError, match="replay exhausted"):
        adapter.observe()


def test_sandbox_mode_accepts_client_state():
    adapter = RuntimeAdapter("sandbox", sandbox_reader=lambda: ClientState(7, {"map": "test"}))
    assert adapter.observe().tick == 7
    assert adapter.connection_ok()
    assert adapter.validate_dry_run()


def test_real_mode_requires_explicit_client_contract():
    with pytest.raises(ValueError, match="injected ClientAdapter"):
        RuntimeAdapter("real")


class FakeClient:
    def check_connection(self): return True
    def read_state(self): return ClientState(8, {"source": "fake"})
    def validate_action(self, action): return action is None
    def close(self): pass


def test_real_mode_is_observation_only():
    adapter = RuntimeAdapter("real", client=FakeClient())
    assert adapter.connection_ok()
    assert adapter.validate_dry_run()
    assert adapter.observe().payload == {"source": "fake"}
