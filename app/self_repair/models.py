"""Data contracts for autonomous repair decisions and telemetry."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Literal

Severity = Literal["INFO", "WARNING", "ERROR", "BLOCKER"]
Operation = Literal["create", "modify", "delete"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ErrorEvent:
    error_id: str
    phase: str
    component: str
    message: str
    severity: Severity = "ERROR"
    exception_type: str | None = None
    traceback: str | None = None
    observed_at: str = field(default_factory=utc_now)
    context: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class FileOperation:
    operation: Operation
    path: str
    content: str | None = None
    reason: str = ""


@dataclass(frozen=True)
class RepairCandidate:
    candidate_id: str
    error_id: str
    hypothesis: str
    operations: tuple[FileOperation, ...]
    expected_improvement: float
    risk: float
    confidence: float
    evidence: tuple[str, ...] = ()

    @property
    def score(self) -> float:
        """Conservative utility score: benefit minus risk."""
        return self.expected_improvement * self.confidence - self.risk


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    score: float
    tests_run: int
    tests_failed: int
    output: str = ""


@dataclass(frozen=True)
class RepairResult:
    error_id: str
    status: Literal["APPLIED", "REJECTED", "BLOCKED", "FAILED"]
    candidate_id: str | None
    validation: ValidationResult | None
    message: str
    completed_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
