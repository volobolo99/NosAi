"""Append-only JSONL replay primitives for real-client observations."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator, Mapping


def append_observation(path: str | Path, observation: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(observation), ensure_ascii=False, sort_keys=True) + "\n")


def iter_observations(path: str | Path) -> Iterator[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid replay JSON at line {line_number}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"replay line {line_number} must contain an object")
            yield value
