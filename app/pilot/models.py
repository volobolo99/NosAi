"""Typed records emitted by the NosAi Test Pilot."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time


class PilotMode(str, Enum):
    """Execution modes; only SIMULATION and SHADOW are enabled by this pilot."""

    SIMULATION = "simulation"
    SHADOW = "shadow"
    DRY_RUN = "dry_run"


class StateQuality(str, Enum):
    """Quality gate for the state presented to the decision engine."""

    VALID = "valid"
    DEGRADED = "degraded"
    UNUSABLE = "unusable"


@dataclass(frozen=True)
class PilotSessionConfig:
    mode: PilotMode = PilotMode.SIMULATION
    ticks: int = 100
    required_capabilities: tuple[str, ...] = (
        "player.position",
        "player.hp",
        "player.mp",
        "entities",
        "target",
    )
    telemetry_path: str = "artifacts/pilot/telemetry.jsonl"


@dataclass(frozen=True)
class PilotError:
    error_id: str
    component: str
    severity: str
    message: str
    recoverable: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    observed_at_ns: int = field(default_factory=time.time_ns)


@dataclass(frozen=True)
class PilotDecision:
    action: Any
    confidence: float
    valid: bool
    validation_reason: str | None = None
    latency_ms: float | None = None


@dataclass(frozen=True)
class PilotResult:
    session_id: str
    mode: PilotMode
    ticks: int
    decisions: int
    valid_decisions: int
    blocked_decisions: int
    state_quality_counts: dict[str, int]
    errors: tuple[PilotError, ...]
    missing_capabilities: tuple[str, ...]
    avg_decision_latency_ms: float | None

    @property
    def ready_for_live_action(self) -> bool:
        """The first Test Pilot is never allowed to authorize live execution."""

        return False
