
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utcnow():
    return datetime.now(timezone.utc)


@dataclass
class Observation:
    id: str
    event_type: str
    payload: dict[str, Any]
    source: str
    timestamp: datetime = field(default_factory=utcnow)
    confidence: float = 1.0
    session_id: str | None = None


@dataclass
class Episode:
    id: str
    session_id: str
    title: str
    observation_ids: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=utcnow)
    ended_at: datetime | None = None
    outcome: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryFact:
    id: str
    subject: str
    predicate: str
    object: Any
    confidence: float
    source_refs: list[str] = field(default_factory=list)
    first_seen: datetime = field(default_factory=utcnow)
    last_verified: datetime = field(default_factory=utcnow)
    verification_count: int = 1


@dataclass
class Inference:
    id: str
    subject: str
    predicate: str
    object: Any
    confidence: float
    supporting_observations: list[str] = field(default_factory=list)
    status: str = "candidate"


@dataclass
class StrategyExperience:
    goal_type: str
    strategy_id: str
    success: bool
    reward: float
    duration_seconds: float
    risk: float
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=utcnow)


@dataclass
class MemoryQuery:
    text: str
    entity_ids: list[str] = field(default_factory=list)
    event_types: list[str] = field(default_factory=list)
    session_id: str | None = None
    limit: int = 20
    min_confidence: float = 0.0
