from __future__ import annotations

import os

import pytest

from app.client import ClientState
from app.client.live_probe_cli import run_probe
from app.client.nostale_windows import NosTaleClientError, WindowsNosTaleAdapter, WindowInfo


def test_adapter_requires_process_name() -> None:
    with pytest.raises(ValueError):
        WindowsNosTaleAdapter([])


def test_adapter_normalizes_process_names_and_allows_only_noop() -> None:
    adapter = WindowsNosTaleAdapter([" NostaleClientX.exe ", "NostaleClientX.exe"])
    assert adapter.process_names == ("nostaleclientx.exe",)
    assert adapter.validate_action(None) is True
    assert adapter.validate_action({"type": "move"}) is False
    adapter.close()


def test_window_info_reports_dimensions_and_area() -> None:
    window = WindowInfo(pid=42, title="NosTale", left=10, top=20, right=1010, bottom=620)
    assert window.width == 1000
    assert window.height == 600
    assert window.area == 600_000


def test_adapter_is_non_destructive_on_non_windows() -> None:
    adapter = WindowsNosTaleAdapter(["NostaleClientX.exe"])
    if os.name == "nt":
        pytest.skip("platform-specific process enumeration")
    assert adapter.check_connection() is False


def test_client_state_contract_remains_normalized() -> None:
    state = ClientState(tick=1, payload={"source": "windows_observation"})
    assert state.payload["source"] == "windows_observation"


def test_probe_is_safe_when_client_is_absent() -> None:
    adapter = WindowsNosTaleAdapter(["__definitely_not_a_real_nostale_process__.exe"])
    result = run_probe(adapter)
    assert result["connected"] is False
    assert result["state_read"] is False
    assert result["observation_only"] is True
    assert result["action_transport"] == "disabled"


def test_read_state_reports_missing_window(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = WindowsNosTaleAdapter(["NostaleClientX.exe"])
    monkeypatch.setattr(adapter, "_find_windows", lambda: [])
    with pytest.raises(NosTaleClientError, match="no visible NosTale client window"):
        adapter.read_state()
