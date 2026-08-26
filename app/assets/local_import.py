"""Import metadata from a user-selected local NosTale client.

Only metadata is persisted by this module. Binary game assets remain in the
user's local client directory and are referenced by relative path + SHA-256.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

from .asset_registry import AssetReference


DEFAULT_FAMILIES = (
    "player",
    "animation",
    "sprite",
    "texture",
    "remap",
    "effect",
    "geometry",
)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def classify_asset(path: Path) -> str:
    name = path.name.lower()
    if "nspndata" in name:
        return "player"
    if "nspcdata" in name or "nsmcdata" in name:
        return "animation"
    if "nspmdata" in name:
        return "remap"
    if "nseffdata" in name or "nseddata" in name or "nsemdata" in name or "nsesdata" in name:
        return "effect"
    if "nstgedata" in name or "nstgdata" in name:
        return "geometry"
    if path.suffix.lower() in {".dds", ".png", ".bmp", ".tga"}:
        return "texture"
    return "sprite"


def scan_local_client(root: str | Path, *, families: Iterable[str] = DEFAULT_FAMILIES) -> list[AssetReference]:
    base = Path(root).resolve()
    allowed = set(families)
    references: list[AssetReference] = []
    if not base.is_dir():
        raise FileNotFoundError(f"client directory does not exist: {base}")

    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        family = classify_asset(path)
        if family not in allowed:
            continue
        relative = path.relative_to(base).as_posix()
        asset_id = hashlib.sha256(relative.encode("utf-8")).hexdigest()[:16]
        references.append(
            AssetReference(
                asset_id=asset_id,
                family=family,
                relative_path=relative,
                sha256=sha256_file(path),
                source="client_locale",
            )
        )
    return references
