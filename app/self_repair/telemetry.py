"""Structured telemetry for first starts and learning cycles.

Telemetry is deliberately append-only and independent from the repair decision.
It records observations that can later be analysed to improve NosAi without
letting runtime data silently change source code.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import uuid


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class CycleObservation:
    cycle_id: str
    phase: str
    status: str
    duration_ms: float | None = None
    metrics: dict[str, float | int | str | bool | None] = field(default_factory=dict)
    error_ids: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    observed_at: str = field(default_factory=_now)


class TelemetryStore:
    """Append observations and provide deterministic summaries for later analysis."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def record(self, observation: CycleObservation) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(observation), ensure_ascii=False, sort_keys=True, default=str) + "\n")

    def start_cycle(self, phase: str, metadata: dict[str, Any] | None = None) -> str:
        cycle_id = uuid.uuid4().hex
        self.record(CycleObservation(cycle_id=cycle_id, phase=phase, status="STARTED", metadata=metadata or {}))
        return cycle_id

    def finish_cycle(
        self,
        cycle_id: str,
        phase: str,
        status: str,
        duration_ms: float | None = None,
        metrics: dict[str, float | int | str | bool | None] | None = None,
        error_ids: tuple[str, ...] = (),
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.record(
            CycleObservation(
                cycle_id=cycle_id,
                phase=phase,
                status=status,
                duration_ms=duration_ms,
                metrics=metrics or {},
                error_ids=error_ids,
                metadata=metadata or {},
            )
        )

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def summary(self) -> dict[str, Any]:
        records = self.read_all()
        finished = [r for r in records if r.get("status") not in {"STARTED"}]
        statuses: dict[str, int] = {}
        errors: set[str] = set()
        for record in finished:
            status = str(record.get("status", "UNKNOWN"))
            statuses[status] = statuses.get(status, 0) + 1
            errors.update(str(item) for item in record.get("error_ids", []))
        return {
            "records": len(records),
            "completed": len(finished),
            "statuses": statuses,
            "unique_error_ids": sorted(errors),
        }
