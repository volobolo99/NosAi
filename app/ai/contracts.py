"""Versioned, dependency-light contracts for the NosAi cognitive pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional, Tuple

CONTRACT_VERSION = "1.0"


class ActionKind(str, Enum):
    NOOP = "noop"
    MOVE = "move"
    ATTACK = "attack"
    USE_SKILL = "use_skill"
    USE_ITEM = "use_item"
    INTERACT = "interact"


@dataclass(frozen=True)
class Goal:
    kind: str
    priority: float = 0.0
    urgency: float = 0.0
    constraints: Tuple[str, ...] = ()
    provenance: str = "system"
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class WorldState:
    timestamp: float
    player_hp_ratio: Optional[float] = None
    player_mp_ratio: Optional[float] = None
    dignity: Optional[float] = None
    distance_to_target: Optional[float] = None
    target_resistance_ratio: Optional[float] = None
    time_remaining: Optional[float] = None
    hardcore_lives: Optional[int] = None
    room_objective: Optional[str] = None
    facts: Mapping[str, Any] = field(default_factory=dict)
    provenance: str = "adapter"
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class ActionIntent:
    kind: ActionKind
    parameters: Mapping[str, Any] = field(default_factory=dict)
    estimated_cost: float = 0.0
    estimated_risk: float = 0.0
    preconditions: Tuple[str, ...] = ()
    source: str = "brain"
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class Decision:
    selected: ActionIntent
    confidence: float
    rationale: str
    alternatives: Tuple[ActionIntent, ...] = ()
    safety_ok: bool = False
    timestamp: float = 0.0
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class Outcome:
    status: str
    state_delta: Mapping[str, Any] = field(default_factory=dict)
    duration: float = 0.0
    evidence_refs: Tuple[str, ...] = ()
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class RewardEvidence:
    components: Mapping[str, float] = field(default_factory=dict)
    source: str = "evaluation"
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class MemoryRecord:
    state_fingerprint: str
    goal: Goal
    intent: ActionIntent
    outcome: Outcome
    reward: RewardEvidence
    provenance: str = "learning_loop"
    contract_version: str = CONTRACT_VERSION
