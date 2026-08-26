from app.assets.asset_manifest import build_manifest, verify_manifest_files
from app.assets.nostale_scanner import AssetFile, ClientDiagnostic, ScannerReport


def report() -> ScannerReport:
    files = (AssetFile("NSpcData.NOS", "player_animations", 12, "a"),)
    diagnostic = ClientDiagnostic("/client", "/client", None, "/client/NostaleData", 1, ("player_animations",), (), "pronto", ())
    return ScannerReport("/client/NostaleData", None, diagnostic, files, None)


def test_manifest_is_portable_and_contains_family_metadata() -> None:
    manifest = build_manifest(report())
    assert manifest.schema_version == "1.0"
    assert manifest.families == ("player_animations",)
    assert manifest.files[0].sha256 == "a"


def test_manifest_verification_does_not_require_copying_assets(tmp_path) -> None:
    manifest = build_manifest(report())
    (tmp_path / "NSpcData.NOS").write_bytes(b"data")
    assert verify_manifest_files(manifest, tmp_path) == ()
