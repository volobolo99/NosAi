from __future__ import annotations

from pathlib import Path

from app.assets.nostale_scanner import NosTaleAssetScanner


def _write(path: Path, data: bytes = b"asset") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def test_diagnostic_accepts_client_root_and_finds_data_and_executable(tmp_path: Path) -> None:
    _write(tmp_path / "NosTale.exe", b"exe")
    _write(tmp_path / "NostaleData" / "NSppData01.NOS")
    _write(tmp_path / "NostaleData" / "NSpcData.NOS")
    _write(tmp_path / "NostaleData" / "NSpmData.NOS")
    _write(tmp_path / "NostaleData" / "NSpnData.NOS")
    _write(tmp_path / "NostaleData" / "NSeffData.NOS")
    _write(tmp_path / "NostaleData" / "NSesData.NOS")
    _write(tmp_path / "NostaleData" / "NStpeData01.NOS")

    report = NosTaleAssetScanner(tmp_path).scan()

    assert report.diagnostic.status == "pronto"
    assert report.diagnostic.executable is not None
    assert report.diagnostic.data_root == str((tmp_path / "NostaleData").resolve())
    assert report.diagnostic.families_missing == ()


def test_diagnostic_accepts_nested_nostaledata_selection(tmp_path: Path) -> None:
    data = tmp_path / "NostaleData"
    _write(data / "NSpcData.NOS")

    report = NosTaleAssetScanner(data).scan()

    assert report.diagnostic.client_root == str(tmp_path.resolve())
    assert report.diagnostic.data_root == str(data.resolve())
    assert "player_animations" in report.diagnostic.families_present
    assert report.diagnostic.status == "incompleto"


def test_diagnostic_never_modifies_selected_client(tmp_path: Path) -> None:
    _write(tmp_path / "NostaleData" / "NSppData01.NOS", b"immutable")
    before = (tmp_path / "NostaleData" / "NSppData01.NOS").read_bytes()

    NosTaleAssetScanner(tmp_path).scan()

    assert (tmp_path / "NostaleData" / "NSppData01.NOS").read_bytes() == before
