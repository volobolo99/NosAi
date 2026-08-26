"""Deterministic evaluation and evidence ledger for simulated decision cycles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from app.nostale_perception.autonomy import ExecutionResult
from app.nostale_perception.skill_ledger import SkillLedger, SkillRecord


@dataclass(frozen=True)
class EvaluationResult:
    skill: str
    success: bool
    score: float
    confidence: float
    reason: str


@dataclass(frozen=True)
class CycleEvidence:
    trace_id: str
    goal: str
    skill: str | None
    outcome: str
    evaluation: EvaluationResult


@dataclass
class EvaluationLedger:
    skill_ledger: SkillLedger = field(default_factory=SkillLedger)
    history: list[CycleEvidence] = field(default_factory=list)

    def evaluate(self, trace_id: str, goal: str, execution: ExecutionResult) -> CycleEvidence:
        if not execution.accepted or not execution.executed:
            evaluation = EvaluationResult(execution.skill, False, 0.0, 0.0, execution.message)
            outcome = "blocked"
        elif execution.success:
            evaluation = EvaluationResult(execution.skill, True, 1.0, 1.0, execution.message)
            outcome = "success"
        else:
            evaluation = EvaluationResult(execution.skill, False, 0.0, 0.5, execution.message)
            outcome = "failure"

        if execution.skill:
            if execution.skill not in self.skill_ledger.skills:
                self.skill_ledger.upsert(SkillRecord(execution.skill, version="1"))
            self.skill_ledger.record_result(execution.skill, evaluation.success, evaluation.confidence)

        evidence = CycleEvidence(trace_id, goal, execution.skill or None, outcome, evaluation)
        self.history.append(evidence)
        return evidence

    def success_rate(self, skills: Iterable[str] | None = None) -> float:
        selected = set(skills) if skills is not None else None
        records = [record for name, record in self.skill_ledger.skills.items() if selected is None or name in selected]
        attempts = sum(record.attempts for record in records)
        successes = sum(record.successes for record in records)
        return successes / attempts if attempts else 0.0
