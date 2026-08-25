from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Sequence
from app.m1.core.types import Action, Prediction, State

@dataclass(frozen=True)
class ImaginedStep:
    state: State
    action: Action
    prediction: Prediction
    cumulative_reward: float
    cumulative_discounted_reward: float
    uncertainty: float

@dataclass(frozen=True)
class ImaginedTrajectory:
    steps: tuple[ImaginedStep, ...]
    total_reward: float
    discounted_return: float
    terminal_probability: float
    uncertainty: float

@dataclass(frozen=True)
class CandidateScore:
    action: Action
    value: float
    risk: float
    uncertainty: float
    visits: int

@dataclass(frozen=True)
class PlanResult:
    actions: tuple[Action, ...]
    value: float
    risk: float
    uncertainty: float
    simulations: int
    candidates: tuple[CandidateScore, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class CounterfactualResult:
    baseline: ImaginedTrajectory
    intervention: ImaginedTrajectory
    delta_return: float
    delta_risk: float
    confidence: float
