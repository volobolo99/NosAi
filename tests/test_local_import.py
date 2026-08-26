from pathlib import Path

from app.assets.local_import import classify_asset, scan_local_client


def test_classify_nostale_asset_families() -> None:
    assert classify_asset(Path("NSpnData.NOS")) == "player"
    assert classify_asset(Path("NSpcData.NOS")) == "animation"
    assert classify_asset(Path("NSpmData.NOS")) == "remap"
    assert classify_asset(Path("NSeffData.NOS")) == "effect"
    assert classify_asset(Path("NStgeData.NOS")) == "geometry"
    assert classify_asset(Path("texture.dds")) == "texture"


def test_scan_local_client_only_records_metadata(tmp_path: Path) -> None:
    root = tmp_path / "NostaleData"
    root.mkdir()
    asset = root / "NSpcData.NOS"
    asset.write_bytes(b"test-asset")

    result = scan_local_client(root)
    assert len(result) == 1
    assert result[0].source == "client_locale"
    assert result[0].relative_path == "NSpcData.NOS"
    assert result[0].sha256
