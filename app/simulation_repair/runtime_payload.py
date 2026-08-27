"""Integrity verification for the offline runtime payload used by sandbox tests."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PayloadFile:
    path: str
    sha256: str
    size: int


@dataclass(frozen=True, slots=True)
class PayloadVerification:
    passed: bool
    checked: int
    failures: tuple[str, ...]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_payload(root: Path, manifest: tuple[PayloadFile, ...]) -> PayloadVerification:
    failures: list[str] = []
    checked = 0
    root = root.resolve()
    for item in manifest:
        candidate = (root / item.path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            failures.append(f"path escapes payload root: {item.path}")
            continue
        if not candidate.is_file():
            failures.append(f"missing payload file: {item.path}")
            continue
        checked += 1
        actual_size = candidate.stat().st_size
        actual_hash = sha256_file(candidate)
        if actual_size != item.size:
            failures.append(f"size mismatch: {item.path}")
        if actual_hash.lower() != item.sha256.lower():
            failures.append(f"sha256 mismatch: {item.path}")
    return PayloadVerification(not failures and checked == len(manifest), checked, tuple(failures))
