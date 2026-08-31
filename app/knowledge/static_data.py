"""Load versioned static NosTale knowledge without silently inventing fields."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator


class StaticDataError(ValueError):
    pass


def iter_records(path: str | Path) -> Iterator[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        raise StaticDataError("static data must contain a records array")
    if not isinstance(payload.get("schema_version"), int):
        raise StaticDataError("schema_version is required")
    source = payload.get("source")
    if not isinstance(source, str) or not source:
        raise StaticDataError("source is required")
    for record in payload["records"]:
        if not isinstance(record, dict):
            raise StaticDataError("each static-data record must be an object")
        if not all(isinstance(record.get(key), str) and record[key] for key in ("id", "kind")):
            raise StaticDataError("record id and kind are required")
        if not isinstance(record.get("fields"), dict):
            raise StaticDataError("record fields must be an object")
        yield record
