from __future__ import annotations

from app.diagnostics.collector import collect_diagnostics, write_report


def test_collect_diagnostics_has_stable_top_level_schema(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.diagnostics.collector._hardware_info",
        lambda: {"query_ok": False},
    )
    monkeypatch.setattr(
        "app.diagnostics.collector.WindowsNosTaleAdapter.check_connection",
        lambda self: False,
    )

    report = collect_diagnostics()

    assert report["schema"] == "nosai.diagnostics.v1"
    assert {"windows", "hardware", "environment", "nostale"} <= report.keys()
    assert report["nostale"]["observation_only"] is True
    assert report["nostale"]["action_transport"] == "disabled"
    serialized = str(report).lower()
    assert "password" not in serialized
    assert "token" not in serialized
    assert "cookie" not in serialized


def test_write_report_creates_utf8_json(tmp_path) -> None:
    target = write_report(tmp_path / "diagnostics.json", {"schema": "test", "text": "NosTale"})

    assert target.exists()
    assert '"schema": "test"' in target.read_text(encoding="utf-8")
