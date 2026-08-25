"""Persistent learning records and safe repair proposals.

This module deliberately does not execute arbitrary generated code. It converts
observed failures into durable, reviewable knowledge and repair tasks. A future
repair provider can consume these tasks and produce a patch that must pass the
normal test gates before it can be applied.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LearningRecord:
    error_id: str
    category: str
    message: str
    scenario: str
    observed_count: int
    first_seen: str
    last_seen: str
    status: str = "observed"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def update_learning_ledger(errors: list[dict[str, Any]], scenario: str, path: str | Path) -> list[LearningRecord]:
    """Merge current-session failures into a durable JSON learning ledger."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    existing: dict[str, dict[str, Any]] = {}
    if target.exists():
        try:
            payload = json.loads(target.read_text(encoding="utf-8"))
            existing = {item["error_id"]: item for item in payload.get("records", [])}
        except (OSError, ValueError, KeyError, TypeError):
            existing = {}

    now = _utc_now()
    for error in errors:
        error_id = str(error.get("error_id", "UNKNOWN"))
        item = existing.get(error_id)
        if item is None:
            existing[error_id] = asdict(
                LearningRecord(
                    error_id=error_id,
                    category=str(error.get("category", error.get("component", "unknown"))),
                    message=str(error.get("message", "")),
                    scenario=scenario,
                    observed_count=1,
                    first_seen=now,
                    last_seen=now,
                )
            )
        else:
            item["observed_count"] = int(item.get("observed_count", 0)) + 1
            item["last_seen"] = now
            item["scenario"] = scenario

    records = [LearningRecord(**value) for value in sorted(existing.values(), key=lambda x: x["error_id"])]
    target.write_text(
        json.dumps({"schema_version": "nosai.learning.v1", "records": [asdict(r) for r in records]}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return records


def write_repair_queue(records: list[LearningRecord], path: str | Path) -> Path:
    """Create a deterministic repair queue for a future code-repair agent."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tasks = [
        {
            "task_id": f"repair-{record.error_id.lower()}",
            "error_id": record.error_id,
            "priority": "high" if record.observed_count >= 3 else "normal",
            "status": "pending",
            "instruction": "Investigate the recorded failure, add a regression test, then propose the smallest safe patch.",
        }
        for record in records
        if record.status == "observed"
    ]
    target.write_text(
        json.dumps({"schema_version": "nosai.repair_queue.v1", "tasks": tasks}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return target
