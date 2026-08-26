from __future__ import annotations

from app.dashboard.observability import scan_repository


def test_observability_scan_builds_file_and_communication_inventory() -> None:
    result = scan_repository()
    assert result["summary"]["source_files"] > 0
    assert result["summary"]["test_files"] > 0
    assert result["summary"]["parse_failures"] == 0
    assert result["summary"]["communication_edges"] > 0
    assert set(result["gates"]) == {"G0", "G1", "G2", "G3", "G4", "G5", "G6"}


def test_not_run_gate_is_explicit() -> None:
    result = scan_repository()
    assert result["gates"]["G2"] == "NOT_RUN"
    assert result["gates"]["G4"] == "NOT_RUN"
