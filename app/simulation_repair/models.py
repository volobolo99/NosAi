"""Stable, JSON-serialisable contracts for simulation/repair evidence."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

SourceKind = Literal["REAL", "CI", "SIMULATED"]
Status = Literal["QUEUED", "RUNNING", "PASS", "FAIL", "ERROR", "NOT_RUN", "READY_FOR_REVIEW"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class ErrorEvent:
    error_id: str
    source: SourceKind
    severity: str
    component: str
    test_name: str
    error_type: str
    message: str
    file: str | None = None
    line: int | None = None
    column: int | None = None
    traceback: str | None = None
    expected: str | None = None
    observed: str | None = None
    fingerprint: str | None = None
    created_at: str = field(default_factory=utc_now)

    @classmethod
    def create(cls, **kwargs: Any) -> "ErrorEvent":
        return cls(error_id=f"ERR-{uuid4().hex[:12].upper()}", **kwargs)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ResearchSource:
    title: str
    url: str
    source_type: str
    relevance: float | None = None
    license: str | None = None
    retrieved_at: str = field(default_factory=utc_now)


@dataclass(slots=True)
class CandidateResult:
    candidate_id: str
    status: Status
    description: str
    evidence: list[str] = field(default_factory=list)
    checks: dict[str, Status] = field(default_factory=dict)
    source_ids: list[str] = field(default_factory=list)
    implementation_ref: str | None = None
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SimulationRun:
    run_id: str
    error_id: str
    status: Status
    phase: str
    progress_percent: int
    candidates: list[CandidateResult] = field(default_factory=list)
    research_sources: list[ResearchSource] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    sealed: bool = False

    @classmethod
    def create(cls, error_id: str) -> "SimulationRun":
        return cls(run_id=f"SIM-{uuid4().hex[:12].upper()}", error_id=error_id, status="QUEUED", phase="queued", progress_percent=0)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
