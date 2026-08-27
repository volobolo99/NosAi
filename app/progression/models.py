from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

SNAPSHOT_SCHEMA = "1.0"

@dataclass(frozen=True)
class CharacterSnapshot:
    snapshot_id: str
    timestamp: float
    server: str | None = None
    channel: str | None = None
    level: int | None = None
    character_class: str | None = None
    progression_milestones: Mapping[str, Any] = field(default_factory=dict)
    stats: Mapping[str, float] = field(default_factory=dict)
    equipment: Mapping[str, Any] = field(default_factory=dict)
    specialist: Mapping[str, Any] = field(default_factory=dict)
    skills: Mapping[str, Any] = field(default_factory=dict)
    resistances: Mapping[str, float] = field(default_factory=dict)
    objectives: tuple[str, ...] = ()
    resources: Mapping[str, float] = field(default_factory=dict)
    inventory: Mapping[str, float] = field(default_factory=dict)
    activity: Mapping[str, Any] = field(default_factory=dict)
    derived: Mapping[str, float] = field(default_factory=dict)
    confidence: float = 1.0
    provenance: str = "runtime"
    schema_version: str = SNAPSHOT_SCHEMA

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.snapshot_id: errors.append("snapshot_id")
        if self.timestamp <= 0: errors.append("timestamp")
        if not 0.0 <= self.confidence <= 1.0: errors.append("confidence")
        if self.schema_version.split(".", 1)[0] != SNAPSHOT_SCHEMA.split(".", 1)[0]: errors.append("schema_version")
        return tuple(errors)

@dataclass(frozen=True)
class ProgressionPlan:
    plan_id: str
    description: str
    steps: tuple[str, ...]
    expected_progress: float
    expected_time_s: float
    resource_cost: float
    risk: float
    policy_status: str = "PASS"
    evidence: tuple[str, ...] = ()

@dataclass(frozen=True)
class PlanResult:
    plan_id: str
    expected_progress: float
    success_probability: float
    expected_time_s: float
    p50_time_s: float
    p90_time_s: float
    resource_cost: float
    risk: float
    confidence: float
    utility: float
    status: str
    reasons: tuple[str, ...] = ()
