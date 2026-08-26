"""Stable domain contracts for the NosAi control plane.

These protocols deliberately contain no provider-specific implementation. External
agents, sandboxes, stores and telemetry systems must adapt to these contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Mapping, Protocol, Sequence
from uuid import UUID, uuid4


class RunState(StrEnum):
    QUEUED = "QUEUED"
    CONTEXT_READY = "CONTEXT_READY"
    PLANNED = "PLANNED"
    EXECUTING = "EXECUTING"
    TESTING = "TESTING"
    VERIFYING = "VERIFYING"
    EVALUATING = "EVALUATING"
    PROMOTABLE = "PROMOTABLE"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True, slots=True)
class RunRecord:
    """Durable identity and audit metadata for one task execution."""

    task_id: str
    source: str
    repository: str
    ref: str
    state: RunState = RunState.QUEUED
    run_id: UUID = field(default_factory=uuid4)
    agent: str | None = None
    model: str | None = None
    instruction_version: str | None = None
    context_manifest: Mapping[str, Any] = field(default_factory=dict)
    sandbox_id: str | None = None
    changed_files: tuple[str, ...] = ()
    test_results: tuple[Mapping[str, Any], ...] = ()
    verification: Mapping[str, Any] | None = None
    evaluation: Mapping[str, Any] | None = None
    metrics: Mapping[str, float] = field(default_factory=dict)
    decision: str | None = None
    failure_reason: str | None = None
    lesson_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class TestResult:
    passed: bool
    name: str
    duration_seconds: float = 0.0
    details: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class VerificationResult:
    passed: bool
    reason: str
    evidence: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    passed: bool
    score: float
    metrics: Mapping[str, float] = field(default_factory=dict)
    reason: str = ""


class TaskSource(Protocol):
    def next_task(self) -> Mapping[str, Any] | None: ...


class RepositoryContextProvider(Protocol):
    def build_context(self, task: Mapping[str, Any], *, repository: str, ref: str) -> Mapping[str, Any]: ...


class AgentExecutor(Protocol):
    def execute(self, task: Mapping[str, Any], context: Mapping[str, Any], *, sandbox_id: str) -> Mapping[str, Any]: ...


class SandboxProvider(Protocol):
    def create(self, *, repository: str, ref: str, run_id: UUID) -> str: ...
    def destroy(self, sandbox_id: str) -> None: ...


class TestRunner(Protocol):
    def run(self, *, sandbox_id: str, changed_files: Sequence[str]) -> Sequence[TestResult]: ...


class Verifier(Protocol):
    def verify(self, *, task: Mapping[str, Any], patch: Mapping[str, Any], sandbox_id: str) -> VerificationResult: ...


class Evaluator(Protocol):
    def evaluate(
        self,
        *,
        task: Mapping[str, Any],
        patch: Mapping[str, Any],
        tests: Sequence[TestResult],
        verification: VerificationResult,
    ) -> EvaluationResult: ...


class ArtifactStore(Protocol):
    def put(self, *, run_id: UUID, name: str, payload: bytes, content_type: str) -> str: ...


class KnowledgeStore(Protocol):
    def record_run(self, run: RunRecord) -> None: ...
    def record_lesson(self, *, run_id: UUID, lesson: Mapping[str, Any]) -> str: ...
    def find_similar(self, *, query: str, limit: int = 5) -> Sequence[Mapping[str, Any]]: ...


class TelemetrySink(Protocol):
    def emit(self, *, event: str, run_id: UUID, attributes: Mapping[str, Any] | None = None) -> None: ...


class PromotionPolicy(Protocol):
    def decide(
        self,
        *,
        run: RunRecord,
        tests: Sequence[TestResult],
        verification: VerificationResult,
        evaluation: EvaluationResult,
    ) -> RunState: ...
