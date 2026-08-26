"""Persistent-in-process evidence for AI shadow decisions."""
from __future__ import annotations

from dataclasses import dataclass, field

from .ai_planner import AIProposal
from .ai_validator import AIValidation
from .planner import DecisionTrace


@dataclass(frozen=True)
class ShadowRecord:
    trace_id: str
    goal: str
    deterministic_skill: str | None
    ai_skill: str | None
    agreement: bool
    ai_confidence: float
    ai_valid: bool
    ai_allowed: bool
    reason: str


@dataclass
class ShadowLedger:
    records: list[ShadowRecord] = field(default_factory=list)

    def record(self, trace: DecisionTrace, proposal: AIProposal, validation: AIValidation) -> ShadowRecord:
        record = ShadowRecord(
            trace.trace_id,
            trace.goal.value,
            trace.selected_skill,
            proposal.skill,
            trace.selected_skill == proposal.skill,
            proposal.confidence,
            validation.valid,
            validation.skill_allowed,
            validation.reason,
        )
        self.records.append(record)
        return record

    @property
    def count(self) -> int:
        return len(self.records)

    def agreement_rate(self) -> float:
        return sum(record.agreement for record in self.records) / self.count if self.count else 0.0

    def valid_rate(self) -> float:
        return sum(record.ai_valid for record in self.records) / self.count if self.count else 0.0
