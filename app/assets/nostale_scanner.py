"""Read-only NosTale asset inventory used by the E2E tests and launcher."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AssetFile:
    path: str
    size: int
    sha256: str
    family: str


@dataclass(frozen=True)
class ScannerDiagnostic:
    status: str
    files_scanned: int
    families_missing: list[str]


@dataclass(frozen=True)
class AssetScanReport:
    root: str
    files: list[AssetFile]
    diagnostic: ScannerDiagnostic
    taletool: str | None = None
    taletool_result: dict[str, Any] | None = None


_FAMILY_RULES = (
    ("NSpn", "player_index"),
    ("NSpc", "player_animations"),
    ("NSpm", "player_remaps"),
    ("NSpp", "player_sprites"),
    ("NSeff", "effect_definitions"),
    ("NStpe", "effect_textures"),
)
_REQUIRED_FAMILIES = {family for _, family in _FAMILY_RULES}


def _family_for(path: Path) -> str | None:
    name = path.name.lower()
    for prefix, family in _FAMILY_RULES:
        if name.startswith(prefix.lower()):
            return family
    return None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class NosTaleAssetScanner:
    """Scan only local files; never modifies the client or executes its assets."""

    def __init__(self, root: str | os.PathLike[str], taletool: str | None = None) -> None:
        self.root = Path(root).expanduser().resolve()
        self.taletool = taletool

    def scan(self) -> AssetScanReport:
        if not self.root.is_dir():
            raise FileNotFoundError(f"NosTale client directory not found: {self.root}")

        files: list[AssetFile] = []
        for path in self.root.rglob("*"):
            if not path.is_file() or path.is_symlink():
                continue
            family = _family_for(path)
            if family is None or path.suffix.lower() != ".nos":
                continue
            try:
                stat = path.stat()
                digest = _sha256(path)
            except OSError:
                continue
            files.append(
                AssetFile(
                    path=path.relative_to(self.root).as_posix(),
                    size=stat.st_size,
                    sha256=digest,
                    family=family,
                )
            )

        files.sort(key=lambda item: item.path.lower())
        present = {item.family for item in files}
        missing = sorted(_REQUIRED_FAMILIES - present)
        diagnostic = ScannerDiagnostic(
            status="pronto" if not missing else "parziale",
            files_scanned=len(files),
            families_missing=missing,
        )
        taletool_result = self._probe_taletool() if self.taletool else None
        return AssetScanReport(
            root=str(self.root),
            files=files,
            diagnostic=diagnostic,
            taletool=self.taletool,
            taletool_result=taletool_result,
        )

    def _probe_taletool(self) -> dict[str, Any] | None:
        path = Path(self.taletool or "")
        if not path.is_absolute():
            path = self.root / path
        if not path.is_file():
            return None
        return {"available": True, "path": str(path)}


def report_json(report: AssetScanReport) -> str:
    """Serialize a scan report using stable JSON keys."""
    return json.dumps(asdict(report), ensure_ascii=False, indent=2, sort_keys=True)
