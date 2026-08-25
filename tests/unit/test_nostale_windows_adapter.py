from __future__ import annotations

import os

import pytest

from app.client import ClientState
from app.client.nostale_windows import WindowsNosTaleAdapter


def test_adapter_requires_process_name() -> None:
    with pytest.raises(ValueError):
        WindowsNosTaleAdapter([])


def test_adapter_accepts_known_nostale_process_names() -> None:
    adapter = WindowsNosTaleAdapter(["NostaleClientX.exe"])
    assert adapter.validate_action(None) is True
    assert adapter.validate_action({"type": "move"}) is False
    adapter.close()


def test_adapter_is_non_destructive_on_non_windows() -> None:
    adapter = WindowsNosTaleAdapter(["NostaleClientX.exe"])
    if os.name == "nt":
        pytest.skip("platform-specific process enumeration")
    assert adapter.check_connection() is False


def test_client_state_contract_remains_normalized() -> None:
    state = ClientState(tick=1, payload={"source": "windows_observation"})
    assert state.payload["source"] == "windows_observation"
