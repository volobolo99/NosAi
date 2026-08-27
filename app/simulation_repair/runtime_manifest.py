"""Deterministic manifest generation for the immutable Windows runtime payload."""
from __future__ import annotations

import hashlib
from pathlib import Path

from .runtime_payload import PayloadFile


def build_manifest(root: Path) -> tuple[PayloadFile, ...]:
    root = root.resolve()
    entries: list[PayloadFile] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        relative = path.relative_to(root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append(PayloadFile(relative, digest, path.stat().st_size))
    return tuple(entries)


def write_manifest(root: Path, destination: Path) -> None:
    lines = [f"{item.sha256}  {item.size}  {item.path}" for item in build_manifest(root)]
    destination.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
