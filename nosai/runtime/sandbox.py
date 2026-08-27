"""Controlled sandbox boundary for G3.6.

The sandbox records proposed runtime commands and produces deterministic
simulated outcomes. It never invokes external processes, input automation,
network control, or real runtime execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from time import monotonic

from .adapter import RuntimeCommand, RuntimeResult


class SessionState(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    CLOSED = "closed"


@dataclass(frozen=True)
class Observation:
    sequence: int
    event: str
    action: str
    accepted: bool


@dataclass(frozen=True)
class AuditEvent:
    sequence: int
    kind: str
    detail: str


class ControlledSandbox:
    """Deterministic, bounded and non-authorizing runtime sandbox."""

    def __init__(self, max_observations: int = 256) -> None:
        if max_observations < 1:
            raise ValueError("max_observations must be positive")
        self._max = max_observations
        self._observations: list[Observation] = []
        self._audit: list[AuditEvent] = []
        self._sequence = 0
        self._state = SessionState.CREATED
        self._kill_switch = True
        self._created_at = monotonic()

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def kill_switch_engaged(self) -> bool:
        return self._kill_switch

    def start(self) -> None:
        if self._state == SessionState.CLOSED:
            raise RuntimeError("sandbox session is closed")
        self._state = SessionState.ACTIVE
        self._record_audit("session.start", "controlled sandbox activated")

    def close(self) -> None:
        self._state = SessionState.CLOSED
        self._record_audit("session.close", "controlled sandbox closed")

    def simulate(self, command: RuntimeCommand) -> RuntimeResult:
        if self._state != SessionState.ACTIVE:
            raise RuntimeError("sandbox session is not active")
        self._sequence += 1
        result = RuntimeResult(True, True, f"sandbox-simulated:{command.action}")
        self._append_observation(Observation(self._sequence, "simulation", command.action, result.accepted))
        self._record_audit("runtime.simulation", command.action)
        return result

    def observations(self) -> tuple[Observation, ...]:
        return tuple(self._observations)

    def audit_events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._audit)

    def _append_observation(self, item: Observation) -> None:
        self._observations.append(item)
        if len(self._observations) > self._max:
            del self._observations[: len(self._observations) - self._max]

    def _record_audit(self, kind: str, detail: str) -> None:
        self._audit.append(AuditEvent(self._sequence, kind, detail))
