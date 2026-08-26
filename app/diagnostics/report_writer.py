"""Write a redaction-safe diagnostic report suitable for support uploads."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_SENSITIVE = {"api_key", "authorization", "token", "password", "secret", "access_token", "refresh_token"}


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: "<REDACTED>" if key.lower() in _SENSITIVE else redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def write_readiness_report(readiness: Any, output: str | Path) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = readiness.to_dict()
    payload["format"] = "nosai-readiness-report-v1"
    path.write_text(json.dumps(redact(payload), indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
