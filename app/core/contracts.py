"""Provider-neutral, serializable contracts shared by NosAi runtime layers.

G1 deliberately contains no live-client or action-execution code. These types
form the stable boundary used by later orchestration, AI, planning and safety
layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Protocol, Sequence


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Evidence:
    source: str
    kind: str = "observation"
    detail: str = ""
    observed_at: datetime = field(default_factory=utc_now)
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("evidence source must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("evidence confidence must be between 0 and 1")


@dataclass(frozen=True)
class WorldState:
    state_id: str
    observed_at: datetime
    values: Mapping[str, Any] = field(default_factory=dict)
    evidence: Sequence[Evidence] = field(default_factory=tuple)
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not self.state_id.strip():
            raise ValueError("state_id must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("state confidence must be between 0 and 1")


@dataclass(frozen=True)
class Goal:
    goal_id: str
    objective: str
    priority: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.goal_id.strip() or not self.objective.strip():
            raise ValueError("goal_id and objective must not be empty")


@dataclass(frozen=True)
class Risk:
    score: float = 1.0
    category: str = "unknown"
    rationale: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("risk score must be between 0 and 1")


@dataclass(frozen=True)
class CandidateAction:
    action_id: str
    action_type: str
    parameters: Mapping[str, Any] = field(default_factory=dict)
    risk: Risk = field(default_factory=Risk)
    preconditions: Sequence[str] = field(default_factory=tuple)
    postconditions: Sequence[str] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.action_id.strip() or not self.action_type.strip():
            raise ValueError("action_id and action_type must not be empty")


class DecisionStatus(str, Enum):
    PROPOSED = "proposed"
    NOOP = "noop"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Decision:
    decision_id: str
    status: DecisionStatus
    action: CandidateAction | None
    rationale: str
    confidence: float
    provider: str
    model: str | None = None
    evidence: Sequence[Evidence] = field(default_factory=tuple)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.decision_id.strip() or not self.provider.strip():
            raise ValueError("decision_id and provider must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("decision confidence must be between 0 and 1")
        if self.status is DecisionStatus.NOOP and self.action is not None:
            raise ValueError("noop decisions cannot contain an action")


@dataclass(frozen=True)
class Outcome:
    outcome_id: str
    decision_id: str
    success: bool
    summary: str = ""
    evidence: Sequence[Evidence] = field(default_factory=tuple)
    observed_at: datetime = field(default_factory=utc_now)


class DecisionProvider(Protocol):
    """Provider-neutral interface for producing a decision from state + goal."""

    name: str

    def decide(self, state: WorldState, goal: Goal) -> Decision:
        ...


def noop_decision(
    *, reason: str = "No action selected", provider: str = "deterministic-noop"
) -> Decision:
    """Return the deterministic, deny-by-default decision used by G1."""
    return Decision(
        decision_id="noop",
        status=DecisionStatus.NOOP,
        action=None,
        rationale=reason,
        confidence=1.0,
        provider=provider,
        model=None,
    )
