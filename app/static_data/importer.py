from __future__ import annotations

import hashlib
import json
import tempfile
import urllib.parse
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
    """Fetch JSON only over explicitly permitted HTTP(S) schemes."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("static data source must use an absolute http(s) URL")
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "NosAi-static-importer/1"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def canonical_json(payload: Any) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
