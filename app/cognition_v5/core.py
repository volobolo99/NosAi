"""Core contracts for the NosAi v5 cognitive loop.

This layer is deliberately deterministic and dependency-light. It can run in
simulation/replay mode and accepts normalized observations instead of knowing
anything about Windows, vision libraries or a concrete client adapter.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from time import monotonic
from typing import Mapping, Sequence


class CognitiveState(StrEnum):
    OBSERVE = "observe"
    EVALUATE = "evaluate"
    PLAN = "plan"
    SELECT = "select"
    EXECUTE = "execute"
    RECOVER = "recover"
    SAFE_STOP = "safe_stop"


@dataclass(frozen=True, slots=True)
class Observation:
    """Normalized perception/event input; no provider-specific objects."""

    kind: str
    value: object
    confidence: float = 1.0
    source: str = "unknown"
    timestamp: float = field(default_factory=monotonic)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class ValueAssessment:
    """Salience, reward and risk signals used by action selection."""

    value: float
    urgency: float = 0.0
    risk: float = 0.0
    novelty: float = 0.0
    rationale: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (("urgency", self.urgency), ("risk", self.risk), ("novelty", self.novelty)):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class ActionCandidate:
    """An intent-level action; low-level input belongs to a separate executor."""

    action_id: str
    expected_value: float
    confidence: float
    risk: float = 0.0
    cost: float = 0.0
    rationale: tuple[str, ...] = ()

    def score(self, risk_weight: float = 1.0, cost_weight: float = 1.0) -> float:
        return self.expected_value * self.confidence - risk_weight * self.risk - cost_weight * self.cost


@dataclass(frozen=True, slots=True)
class SafetyDecision:
    allowed: bool
    reason: str
    severity: int = 0


@dataclass(frozen=True, slots=True)
class CognitiveCycle:
    state: CognitiveState
    selected_action: ActionCandidate | None
    value: ValueAssessment
    safety: SafetyDecision
    rationale: tuple[str, ...] = ()


class ExecutiveController:
    """Small orchestration core for the v5 decision cycle.

    It does not execute client actions. It evaluates candidates, applies the
    safety gate and returns an intent that an external executor may handle.
    """

    def __init__(self, *, risk_weight: float = 1.0, cost_weight: float = 1.0) -> None:
        if risk_weight < 0 or cost_weight < 0:
            raise ValueError("weights cannot be negative")
        self.risk_weight = risk_weight
        self.cost_weight = cost_weight

    @staticmethod
    def assess_value(observations: Sequence[Observation]) -> ValueAssessment:
        if not observations:
            return ValueAssessment(value=0.0, rationale=("no observations",))
        confidence = sum(o.confidence for o in observations) / len(observations)
        urgent = any(o.kind in {"critical", "danger", "disconnect"} for o in observations)
        return ValueAssessment(
            value=confidence,
            urgency=1.0 if urgent else 0.0,
            risk=1.0 if any(o.kind in {"danger", "critical"} for o in observations) else 0.0,
            novelty=1.0 if any(o.kind == "novel" for o in observations) else 0.0,
            rationale=(f"aggregated {len(observations)} normalized observations",),
        )

    @staticmethod
    def safety_gate(value: ValueAssessment) -> SafetyDecision:
        if value.risk >= 1.0:
            return SafetyDecision(False, "critical risk signal", severity=3)
        return SafetyDecision(True, "no critical safety condition", severity=0)

    def select_action(self, candidates: Sequence[ActionCandidate]) -> ActionCandidate | None:
        if not candidates:
            return None
        return max(candidates, key=lambda c: c.score(self.risk_weight, self.cost_weight))

    def cycle(
        self,
        observations: Sequence[Observation],
        candidates: Sequence[ActionCandidate],
    ) -> CognitiveCycle:
        value = self.assess_value(observations)
        safety = self.safety_gate(value)
        if not safety.allowed:
            return CognitiveCycle(CognitiveState.SAFE_STOP, None, value, safety, (safety.reason,))
        selected = self.select_action(candidates)
        state = CognitiveState.SELECT if selected else CognitiveState.PLAN
        rationale = (f"selected={selected.action_id}" if selected else "no viable action",)
        return CognitiveCycle(state, selected, value, safety, rationale)
