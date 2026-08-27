"""Provider-neutral contracts for NosAI memory and durable execution state."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MemoryType(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class MemoryScope(str, Enum):
    RUN = "run"
    SESSION = "session"
    PROFILE = "profile"
    GLOBAL = "global"


@dataclass(frozen=True)
class MemoryItem:
    id: str
    memory_type: MemoryType
    scope: MemoryScope
    content: str
    created_at: str
    updated_at: str
    provenance: tuple[str, ...] = ()
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id or not self.content:
            raise ValueError("memory id and content are required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class StateRecord:
    run_id: str
    status: str
    version: int
    updated_at: str
    data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.run_id:
            raise ValueError("run_id is required")
        if self.version < 0:
            raise ValueError("version must be non-negative")
