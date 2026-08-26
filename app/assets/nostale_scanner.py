"""Safe, local-only discovery of NosTale client asset families.

The scanner never downloads or modifies game files. It inspects the user-selected
client data directory and can optionally call an installed Taletool executable
for format-aware classification. Proprietary extracted assets stay outside Git.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

FAMILY_PATTERNS: dict[str, tuple[str, ...]] = {
    "player_sprites": ("NSppData*.NOS",),
    "player_animations": ("NSpcData.NOS",),
    "player_remaps": ("NSpmData.NOS",),
    "player_index": ("NSpnData.NOS",),
    "player_textures": ("NStpData*.NOS",),
    "effect_definitions": ("NSeffData.NOS",),
    "effect_color_animation": ("NSedData.NOS",),
    "effect_transform_animation": ("NSemData.NOS",),
    "effect_texture_animation": ("NSesData.NOS",),
    "effect_geometry": ("NStgeData.NOS",),
    "effect_textures": ("NStpeData*.NOS",),
    "map_item_sprites": ("NSipData.NOS",),
    "monster_npc_sprites": ("NSmpData*.NOS",),
    "monster_npc_animations": ("NSmcData.NOS",),
    "monster_npc_index": ("NSmnData.NOS",),
    "geometry": ("NStgData*.NOS",),
}


@dataclass(frozen=True)
class AssetFile:
    path: str
    family: str
    size: int
    sha256: str


@dataclass(frozen=True)
class ScannerReport:
    data_dir: str
    taletool: str | None
    files: tuple[AssetFile, ...]
    taletool_result: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "data_dir": self.data_dir,
            "taletool": self.taletool,
            "files": [asdict(item) for item in self.files],
            "taletool_result": self.taletool_result,
        }


class NosTaleAssetScanner:
    """Discover only files needed by the NosAi avatar/effect renderer."""

    def __init__(self, data_dir: str | Path, taletool: str | None = None) -> None:
        self.data_dir = Path(data_dir).expanduser().resolve()
        if not self.data_dir.is_dir():
            raise FileNotFoundError(f"directory NosTale non trovata: {self.data_dir}")
        self.taletool = taletool or shutil.which("taletool")

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    @staticmethod
    def _matches(filename: str, pattern: str) -> bool:
        regex = re.escape(pattern).replace(r"\*", ".*").replace(r"\?", ".")
        return re.fullmatch(regex, filename, flags=re.IGNORECASE) is not None

    def _family_for(self, filename: str) -> str | None:
        for family, patterns in FAMILY_PATTERNS.items():
            if any(self._matches(filename, pattern) for pattern in patterns):
                return family
        return None

    def discover(self) -> tuple[AssetFile, ...]:
        found: list[AssetFile] = []
        for path in sorted(self.data_dir.rglob("*")):
            if not path.is_file():
                continue
            family = self._family_for(path.name)
            if family is None:
                continue
            found.append(
                AssetFile(
                    path=path.relative_to(self.data_dir).as_posix(),
                    family=family,
                    size=path.stat().st_size,
                    sha256=self._sha256(path),
                )
            )
        return tuple(found)

    def inspect_with_taletool(self, timeout_s: float = 60.0) -> dict[str, Any] | None:
        if not self.taletool:
            return None
        command = [self.taletool, "scan", "--data-dir", os.fspath(self.data_dir), "--json"]
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_s,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return {"ok": False, "errore": str(exc)}
        try:
            payload = json.loads(completed.stdout) if completed.stdout.strip() else None
        except json.JSONDecodeError:
            payload = None
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "risultato": payload,
            "stderr": completed.stderr[-4000:],
        }

    def scan(self) -> ScannerReport:
        return ScannerReport(
            data_dir=os.fspath(self.data_dir),
            taletool=self.taletool,
            files=self.discover(),
            taletool_result=self.inspect_with_taletool(),
        )


def report_json(report: ScannerReport) -> str:
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
