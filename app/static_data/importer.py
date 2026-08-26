from __future__ import annotations

import hashlib
import http.client
import json
import tempfile
import urllib.parse
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
    """Fetch JSON over an explicitly permitted HTTP(S) URL without redirects."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("static data source must use an absolute http(s) URL")
    if parsed.username or parsed.password:
        raise ValueError("static data source must not contain URL credentials")
    if parsed.fragment:
        raise ValueError("static data source must not contain a URL fragment")

    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    connection_cls = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    connection = connection_cls(host, port=port, timeout=timeout)
    try:
        path = parsed.path or "/"
        if parsed.query:
            path += f"?{parsed.query}"
        connection.request(
            "GET",
            path,
            headers={"Accept": "application/json", "User-Agent": "NosAi-static-importer/1"},
        )
        response = connection.getresponse()
        if response.status < 200 or response.status >= 300:
            raise ValueError(f"static data source returned HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))
    finally:
        connection.close()


def canonical_json(payload: Any) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
