"""Create deterministic metadata for imported source snapshots."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


def snapshot_digest(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def build_snapshot(*, source_id: str, source_ref: str, payload: Mapping[str, Any], version: str | None = None, commit: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "source_id": source_id,
        "source_ref": source_ref,
        "version": version,
        "commit": commit,
        "sha256": snapshot_digest(payload),
    }
