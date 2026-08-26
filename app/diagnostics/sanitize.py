"""Sanitize NosAi diagnostic reports before sharing them."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_WINDOWS_USER = re.compile(r"(?i)([A-Z]:\\Users\\)[^\\]+")
_UNIX_HOME = re.compile(r"/home/[^/]+")


def sanitize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: sanitize_value(val) for key, val in value.items() if key.lower() not in {"username", "user_name", "email", "token", "password"}}
    if isinstance(value, list):
        return [sanitize_value(item) for item in value]
    if isinstance(value, str):
        value = _WINDOWS_USER.sub(r"\1<USER>", value)
        return _UNIX_HOME.sub("/home/<USER>", value)
    return value


def sanitize_report(input_path: str | Path, output_path: str | Path) -> Path:
    source = Path(input_path).expanduser().resolve()
    target = Path(output_path).expanduser().resolve()
    payload = json.loads(source.read_text(encoding="utf-8"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(sanitize_value(payload), ensure_ascii=False, indent=2), encoding="utf-8")
    return target
