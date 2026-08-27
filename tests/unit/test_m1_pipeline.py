from pathlib import Path

from app.simulation_repair.m1_pipeline import preflight_payload


def test_m1_preflight_rejects_empty_payload(tmp_path: Path) -> None:
    result = preflight_payload(tmp_path)
    assert result.manifest_entries == 0
    assert result.ready_for_windows_execution is False


def test_m1_preflight_accepts_self_consistent_payload(tmp_path: Path) -> None:
    (tmp_path / "runtime.txt").write_text("NosAi runtime\n", encoding="utf-8")
    result = preflight_payload(tmp_path)
    assert result.manifest_entries == 1
    assert result.payload.passed is True
    assert result.ready_for_windows_execution is True
