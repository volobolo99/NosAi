"""Append-only telemetry journal for first-start and learning-cycle analysis."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from threading import Lock

from .models import ErrorEvent, RepairCandidate, RepairResult


class RepairJournal:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._lock = Lock()

    def record(self, kind: str, payload: ErrorEvent | RepairCandidate | RepairResult | dict[str, object]) -> None:
        data = asdict(payload) if hasattr(payload, "__dataclass_fields__") else payload
        entry = {"kind": kind, "payload": data}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock, self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True, default=str) + "\n")

    def read_all(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
