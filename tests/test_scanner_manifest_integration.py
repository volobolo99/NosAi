from app.assets.asset_manifest import build_manifest, verify_manifest_files
from app.assets.nostale_scanner import NosTaleAssetScanner


def test_scanner_finds_real_format_families_and_manifest(tmp_path):
    data = tmp_path / "NostaleData"
    data.mkdir()
    for name in (
        "NSpcData.NOS", "NSpmData.NOS", "NSpnData.NOS", "NSppData01.NOS",
        "NStpData01.NOS", "NSeffData.NOS", "NSedData.NOS", "NSesData.NOS", "NStpeData01.NOS",
    ):
        (data / name).write_bytes(name.encode())
    (tmp_path / "NosTale.exe").write_bytes(b"MZ")

    report = NosTaleAssetScanner(tmp_path).scan()
    assert report.diagnostic.status == "pronto"
    manifest = build_manifest(report)
    assert {"player_animations", "player_remaps", "player_index"}.issubset(manifest.families)
    assert verify_manifest_files(manifest, data) == ()
