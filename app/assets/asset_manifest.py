"""Portable manifest generation for locally discovered NosTale assets."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from .nostale_scanner import AssetFile, ScannerReport


@dataclass(frozen=True)
class AssetManifest:
    schema_version: str
    client_root: str
    data_root: str
    files: tuple[AssetFile, ...]
    families: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def build_manifest(report: ScannerReport) -> AssetManifest:
    families = tuple(sorted({asset.family for asset in report.files}))
    return AssetManifest(
        schema_version="1.0",
        client_root=report.diagnostic.client_root,
        data_root=report.data_dir,
        files=report.files,
        families=families,
    )


def write_manifest(manifest: AssetManifest, output: str | Path) -> Path:
    target = Path(output).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def verify_manifest_files(manifest: AssetManifest, root: str | Path) -> tuple[str, ...]:
    """Return missing manifest paths without touching or copying source assets."""
    base = Path(root).expanduser().resolve()
    return tuple(asset.path for asset in manifest.files if not (base / asset.path).is_file())
