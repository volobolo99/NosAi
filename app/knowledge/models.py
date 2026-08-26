"""Domain models for the NosAi knowledge graph.

The graph is intentionally source/evidence first: a node can be useful before it is
confirmed, but its confidence and provenance are always explicit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class NodeType(StrEnum):
    BUG = "bug"
    GLITCH = "glitch"
    ANOMALY = "anomaly"
    PACKET = "packet"
    EVENT = "event"
    GAME_STATE = "game_state"
    MAP = "map"
    NPC = "npc"
    QUEST = "quest"
    SKILL = "skill"
    ITEM = "item"
    SOURCE = "source"
    VERSION = "version"
    TEST_CASE = "test_case"
    OBSERVATION = "observation"
    FIX = "fix"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class Evidence:
    source_id: str
    url: str | None = None
    quote: str | None = None
    observed_at: str | None = None
    version: str | None = None
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("evidence confidence must be between 0 and 1")


@dataclass(slots=True)
class KnowledgeNode:
    id: str
    type: NodeType
    title: str
    description: str = ""
    status: str = "unknown"
    confidence: float = 0.0
    properties: dict[str, Any] = field(default_factory=dict)
    evidence: list[Evidence] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("node id cannot be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("node confidence must be between 0 and 1")


@dataclass(slots=True)
class Edge:
    id: str
    source_id: str
    relation: str
    target_id: str
    confidence: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.source_id.strip() or not self.target_id.strip():
            raise ValueError("edge ids and endpoints cannot be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("edge confidence must be between 0 and 1")
