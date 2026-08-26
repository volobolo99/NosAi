"""Provider-neutral contracts for the ZMSIA control loop.

These dataclasses are intentionally small, immutable and JSON-friendly. They
are the boundary between the existing NosAi modules and future local/OpenAI
providers. Domain-specific modules should adapt to these contracts instead of
importing a provider implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Status = Literal["ok", "failed", "rejected", "timeout", "cancelled"]


@dataclass(frozen=True)
class Observation:
    """Raw or normalized evidence produced by a perception adapter."""

    observation_id: str
    timestamp_ms: int
    source: str
    data: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    schema_version: int = 1


@dataclass(frozen=True)
class State:
    """Normalized world state derived from one or more observations."""

    state_id: str
    timestamp_ms: int
    values: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    source_observation_ids: tuple[str, ...] = ()
    schema_version: int = 1


@dataclass(frozen=True)
class Plan:
    """Provider-neutral plan proposed for a goal."""

    plan_id: str
    goal_id: str
    steps: tuple[str, ...]
    rationale: str = ""
    confidence: float = 0.0
    provider: str = "unknown"
    schema_version: int = 1


@dataclass(frozen=True)
class Decision:
    """A proposed action decision before validation and safety checks."""

    decision_id: str
    goal_id: str
    action_id: str
    parameters: dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    confidence: float = 0.0
    provider: str = "unknown"
    plan_id: str | None = None
    schema_version: int = 1


@dataclass(frozen=True)
class Action:
    """Validated executable intent; never represents an unchecked tool call."""

    action_id: str
    parameters: dict[str, Any] = field(default_factory=dict)
    decision_id: str = ""
    schema_version: int = 1


@dataclass(frozen=True)
class SafetyDecision:
    """Result of policy validation before an action reaches an executor."""

    allowed: bool
    reason: str
    policy_version: str
    risk_score: float = 0.0
    required_mode: str = "safe"
    schema_version: int = 1


@dataclass(frozen=True)
class ActionResult:
    """Deterministic result returned by an action executor."""

    action_id: str
    status: Status
    timestamp_ms: int
    output: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None
    schema_version: int = 1


@dataclass(frozen=True)
class ToolRequest:
    """Capability request sent through the Tool Gateway."""

    request_id: str
    tool: str
    operation: str
    arguments: dict[str, Any] = field(default_factory=dict)
    timeout_ms: int = 5000
    dry_run: bool = True
    schema_version: int = 1


@dataclass(frozen=True)
class ToolResult:
    """Sanitized Tool Gateway response."""

    request_id: str
    status: Status
    output: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None
    duration_ms: int = 0
    schema_version: int = 1


@dataclass(frozen=True)
class EvaluationResult:
    """Evidence used to accept or reject a decision, action or change."""

    evaluation_id: str
    subject_id: str
    passed: bool
    score: float
    metrics: dict[str, float] = field(default_factory=dict)
    evaluator: str = "unknown"
    baseline_id: str | None = None
    schema_version: int = 1


@dataclass(frozen=True)
class ErrorEvent:
    """Structured failure evidence suitable for diagnostics and memory."""

    event_id: str
    timestamp_ms: int
    component: str
    code: str
    message: str
    recoverable: bool = True
    context: dict[str, Any] = field(default_factory=dict)
    schema_version: int = 1
