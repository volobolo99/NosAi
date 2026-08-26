from __future__ import annotations

import json
from pathlib import Path

from app.assets.nostale_scanner import NosTaleAssetScanner, report_json


def test_scanner_classifies_renderer_families_and_hashes_files(tmp_path: Path) -> None:
    (tmp_path / "NSpcData.NOS").write_bytes(b"player-animation")
    (tmp_path / "NSpmData.NOS").write_bytes(b"player-remap")
    (tmp_path / "NSppData01.NOS").write_bytes(b"player-sprite")
    (tmp_path / "NSeffData.NOS").write_bytes(b"effects")
    (tmp_path / "NStpeData02.NOS").write_bytes(b"effect-texture")
    (tmp_path / "unrelated.bin").write_bytes(b"ignore")

    report = NosTaleAssetScanner(tmp_path, taletool="__missing_taletool__").scan()
    families = {item.family for item in report.files}
    assert families == {
        "player_animations",
        "player_remaps",
        "player_sprites",
        "effect_definitions",
        "effect_textures",
    }
    assert all(len(item.sha256) == 64 for item in report.files)
    assert report.taletool_result is None


def test_report_is_machine_readable(tmp_path: Path) -> None:
    (tmp_path / "NSpnData.NOS").write_bytes(b"index")
    report = NosTaleAssetScanner(tmp_path, taletool="__missing_taletool__").scan()
    payload = json.loads(report_json(report))
    assert payload["files"][0]["family"] == "player_index"
