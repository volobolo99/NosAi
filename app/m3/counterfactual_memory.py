from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid

@dataclass(frozen=True)
class CounterfactualRecord:
    id: str
    context: dict[str, Any]
    intervention: dict[str, Any]
    baseline: float
    counterfactual: float
    delta: float
    confidence: float
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class CounterfactualMemory:
    def __init__(self, max_records: int = 10000):
        self.max_records = max_records
        self.records: list[CounterfactualRecord] = []

    def add(self, context, intervention, baseline, counterfactual, confidence=1.0):
        rec = CounterfactualRecord(str(uuid.uuid4()), dict(context), dict(intervention), float(baseline), float(counterfactual), float(counterfactual-baseline), float(confidence))
        self.records.append(rec)
        if len(self.records) > self.max_records:
            self.records.pop(0)
        return rec

    def query(self, intervention: dict[str, Any] | None = None, limit: int = 20):
        rows = self.records
        if intervention:
            rows = [r for r in rows if all(r.intervention.get(k) == v for k, v in intervention.items())]
        return list(reversed(rows[-limit:]))

    def mean_effect(self, intervention: dict[str, Any]) -> float | None:
        rows = self.query(intervention, limit=self.max_records)
        return sum(r.delta * r.confidence for r in rows) / sum(r.confidence for r in rows) if rows else None
