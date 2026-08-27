from __future__ import annotations

from app.runtime import windows_adapter


def test_snapshot_has_runtime_contract(monkeypatch) -> None:
    monkeypatch.setattr(windows_adapter, "_find_nostale_processes", lambda: (1234,))
    snap = windows_adapter.snapshot()
    data = snap.to_dict()
    assert data["client_detected"] is True
    assert data["client_pids"] == (1234,)
    assert data["cpu_threads"] >= 1


def test_non_windows_process_discovery_is_read_only(monkeypatch) -> None:
    monkeypatch.setattr(windows_adapter.os, "name", "posix")
    assert windows_adapter._find_nostale_processes() == ()
