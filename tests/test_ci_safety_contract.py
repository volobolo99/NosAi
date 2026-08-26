"""CI-level regression tests for the live-client safety boundary."""

from dataclasses import fields

import pytest

from app.client.adapter import ClientAdapter, ClientState, validate_adapter


class _CompleteAdapter:
    def check_connection(self):
        return True

    def read_state(self):
        return ClientState(tick=1, payload={})

    def validate_action(self, action):
        return False

    def close(self):
        return None


def test_client_state_contract_is_minimal_and_stable():
    assert [field.name for field in fields(ClientState)] == ["tick", "payload"]
    assert ClientState(tick=7, payload={"source": "test"}).tick == 7


def test_complete_adapter_satisfies_runtime_protocol():
    adapter = _CompleteAdapter()
    assert isinstance(adapter, ClientAdapter)
    validate_adapter(adapter)


def test_incomplete_adapter_fails_before_live_use():
    class Incomplete:
        def check_connection(self):
            return True

    with pytest.raises(TypeError, match="missing required methods"):
        validate_adapter(Incomplete())


def test_action_validation_is_explicit_and_non_execution_by_contract():
    adapter = _CompleteAdapter()
    action = object()
    assert adapter.validate_action(action) is False
    assert not hasattr(adapter, "execute_action")
    assert not hasattr(adapter, "send_input")
