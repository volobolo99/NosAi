"""Load bundled NosTale source and packet knowledge manifests."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SOURCE_MANIFEST = ROOT / "data" / "sources" / "nostale_sources.json"
PACKET_CATALOG = ROOT / "data" / "packets" / "verified_packet_catalog.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Knowledge manifest must be an object: {path}")
    return value


def load_source_manifest() -> dict[str, Any]:
    return load_json(SOURCE_MANIFEST)


def load_packet_catalog() -> dict[str, Any]:
    return load_json(PACKET_CATALOG)


def packet_headers() -> tuple[str, ...]:
    catalog = load_packet_catalog()
    return tuple(item["header"] for item in catalog.get("packets", []) if item.get("header"))
