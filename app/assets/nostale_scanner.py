"""Safe, local-only discovery and diagnostics for a NosTale client.

The scanner never downloads or modifies game files. It inspects a user-selected
client directory, identifies the executable/data root, inventories the asset
families needed by the avatar/effect renderer, and optionally invokes an
installed Taletool executable.
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
from typing import Any

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

REQUIRED_FAMILIES = {
    "player_sprites", "player_animations", "player_remaps", "player_index",
}


@dataclass(frozen=True)
class AssetFile:
    path: str
    family: str
    size: int
    sha256: str


@dataclass(frozen=True)
class ClientDiagnostic:
    selected_path: str
    client_root: str
    executable: str | None
    data_root: str | None
    files_found: int
    families_present: tuple[str, ...]
    families_missing: tuple[str, ...]
    status: str
    messages: tuple[str, ...]


@dataclass(frozen=True)
class ScannerReport:
    data_dir: str
    taletool: str | None
    diagnostic: ClientDiagnostic
    files: tuple[AssetFile, ...]
    taletool_result: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "data_dir": self.data_dir,
            "taletool": self.taletool,
            "diagnostic": asdict(self.diagnostic),
            "files": [asdict(item) for item in self.files],
            "taletool_result": self.taletool_result,
        }


class NosTaleAssetScanner:
    """Discover and validate only files needed by the NosAi renderer."""

    def __init__(self, selected_path: str | Path, taletool: str | None = None) -> None:
        self.selected_path = Path(selected_path).expanduser().resolve()
        if not self.selected_path.is_dir():
            raise FileNotFoundError(f"directory NosTale non trovata: {self.selected_path}")
        self.client_root = self._find_client_root(self.selected_path)
        self.data_dir = self._find_data_root(self.client_root)
        self.executable = self._find_executable(self.client_root)
        self.taletool = taletool or shutil.which("taletool")

    @staticmethod
    def _find_client_root(selected: Path) -> Path:
        if (selected / "NostaleData").is_dir() or any(selected.glob("NosTale*.exe")):
            return selected
        for candidate in (selected, *selected.parents):
            if (candidate / "NostaleData").is_dir() or any(candidate.glob("NosTale*.exe")):
                return candidate
        return selected

    @staticmethod
    def _find_data_root(root: Path) -> Path | None:
        candidates = [root / "NostaleData", root / "NostaleData" / "data"]
        candidates.extend(path for path in root.iterdir() if path.is_dir() and path.name.lower() == "nostaledata")
        for candidate in candidates:
            if candidate.is_dir():
                return candidate
        return root if any(root.rglob("*.NOS")) else None

    @staticmethod
    def _find_executable(root: Path) -> str | None:
        for name in ("NosTaleClient.exe", "NosTale.exe", "Nostale.exe"):
            candidate = root / name
            if candidate.is_file():
                return os.fspath(candidate)
        for candidate in sorted(root.glob("*.exe")):
            if "nostale" in candidate.name.lower():
                return os.fspath(candidate)
        return None

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
        root = self.data_dir or self.client_root
        found: list[AssetFile] = []
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            family = self._family_for(path.name)
            if family is None:
                continue
            found.append(AssetFile(path.relative_to(root).as_posix(), family, path.stat().st_size, self._sha256(path)))
        return tuple(found)

    def diagnose(self, files: tuple[AssetFile, ...]) -> ClientDiagnostic:
        present = tuple(sorted({item.family for item in files}))
        missing = tuple(sorted(REQUIRED_FAMILIES - set(present)))
        messages = []
        messages.append("eseguibile NosTale rilevato" if self.executable else "eseguibile NosTale non trovato nella cartella selezionata")
        messages.append(f"radice dati rilevata: {self.data_dir}" if self.data_dir else "NostaleData non rilevata")
        if missing:
            messages.append("famiglie asset richieste mancanti: " + ", ".join(missing))
        return ClientDiagnostic(
            os.fspath(self.selected_path), os.fspath(self.client_root), self.executable,
            os.fspath(self.data_dir) if self.data_dir else None, len(files), present, missing,
            "pronto" if not missing else "incompleto", tuple(messages)
        )

    def inspect_with_taletool(self, timeout_s: float = 60.0) -> dict[str, Any] | None:
        if not self.taletool:
            return None
        root = self.data_dir or self.client_root
        command = [self.taletool, "scan", "--data-dir", os.fspath(root), "--json"]
        try:
            completed = subprocess.run(command, check=False, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout_s)
        except (OSError, subprocess.SubprocessError) as exc:
            return {"ok": False, "errore": str(exc)}
        try:
            payload = json.loads(completed.stdout) if completed.stdout.strip() else None
        except json.JSONDecodeError:
            payload = None
        return {"ok": completed.returncode == 0, "returncode": completed.returncode, "risultato": payload, "stderr": completed.stderr[-4000:]}

    def scan(self) -> ScannerReport:
        files = self.discover()
        return ScannerReport(os.fspath(self.data_dir or self.client_root), self.taletool, self.diagnose(files), files, self.inspect_with_taletool())


def report_json(report: ScannerReport) -> str:
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
