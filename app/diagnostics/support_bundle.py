"""Build a redaction-safe diagnostic bundle from a startup report."""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from .startup_check import StartupReport


REDACTED_KEYS = {"api_key", "authorization", "token", "password", "secret"}


def _redact(value: object) -> object:
    if isinstance(value, dict):
        return {k: "<REDACTED>" if k.lower() in REDACTED_KEYS else _redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def write_support_bundle(report: StartupReport, output: str | Path) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _redact(asdict(report))
    payload["format"] = "nosai-support-bundle-v1"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
