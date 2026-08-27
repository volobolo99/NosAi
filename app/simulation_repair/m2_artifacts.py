"""Deterministic artifact bundle for the M2 simulation gate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_artifacts(root: Path, *, patterns: Iterable[str] = ("*.json", "*.log")) -> list[dict[str, object]]:
    root = root.resolve()
    items: list[dict[str, object]] = []
    seen: set[Path] = set()
    for pattern in patterns:
        for path in sorted(root.rglob(pattern)):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            relative = path.relative_to(root).as_posix()
            items.append({"path": relative, "size": path.stat().st_size, "sha256": sha256_file(path)})
    return items


def write_artifact_index(root: Path, destination: Path) -> None:
    payload = {"schema_version": "1.0", "artifacts": collect_artifacts(root)}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
