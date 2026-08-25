from __future__ import annotations

import hashlib
import json
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .manifest import StaticManifest


@dataclass(frozen=True)
class ImportedSnapshot:
    dataset: str
    source: str
    version: str
    sha256: str
    path: Path


def fetch_json(url: str, *, timeout: float = 20.0) -> Any:
    """Fetch one JSON source during the offline import/build phase."""
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "NosAi-static-importer/1"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
        return json.load(response)


def canonical_json(payload: Any) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_snapshot(root: Path, dataset: str, payload: Any) -> tuple[Path, str]:
    """Write atomically so a failed import can never leave a partial snapshot."""
    root.mkdir(parents=True, exist_ok=True)
    data = canonical_json(payload)
    digest = sha256_bytes(data)
    target = root / f"{dataset}.json"
    with tempfile.NamedTemporaryFile("wb", dir=root, delete=False) as tmp:
        tmp.write(data)
        tmp.flush()
        temp_path = Path(tmp.name)
    temp_path.replace(target)
    return target, digest


def validate_required_sources(manifest: StaticManifest) -> None:
    missing = [d.name for d in manifest.datasets if d.required and not d.source]
    if missing:
        raise ValueError("required static-data sources are not configured: " + ", ".join(missing))


def import_sources(manifest: StaticManifest, output_dir: Path) -> list[ImportedSnapshot]:
    """Import configured JSON sources and return verified local snapshots.

    The function intentionally refuses unconfigured sources. It must be run before
    gameplay and never from the client runtime loop.
    """
    validate_required_sources(manifest)
    results: list[ImportedSnapshot] = []
    for dataset in manifest.datasets:
        if not dataset.source:
            continue
        payload = fetch_json(dataset.source)
        path, digest = write_snapshot(output_dir, dataset.name, payload)
        version = dataset.version or "unversioned"
        if dataset.sha256 and dataset.sha256 != digest:
            raise ValueError(f"checksum mismatch for {dataset.name}: expected {dataset.sha256}, got {digest}")
        results.append(ImportedSnapshot(dataset.name, dataset.source, version, digest, path))
    return results
