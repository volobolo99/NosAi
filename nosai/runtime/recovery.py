"""Deterministic runtime session state and safe recovery for G3.10."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SessionState(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    DEGRADED = "degraded"
    RECOVERING = "recovering"
    SAFE = "safe"
    CLOSED = "closed"


@dataclass(frozen=True)
class RecoveryEvent:
    state: SessionState
    reason: str


class RuntimeRecovery:
    """Fail-closed state machine; recovery can never enable real execution."""

    def __init__(self) -> None:
        self._state = SessionState.CREATED
        self._events: list[RecoveryEvent] = []
        self._kill_switch = True

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def kill_switch_engaged(self) -> bool:
        return self._kill_switch

    def start(self) -> None:
        self._transition(SessionState.ACTIVE, "session started")

    def fault(self, reason: str) -> None:
        if not reason.strip():
            raise ValueError("reason must be non-empty")
        self._transition(SessionState.DEGRADED, reason)

    def recover(self) -> None:
        if self._state is not SessionState.DEGRADED:
            raise RuntimeError("recovery requires degraded state")
        self._transition(SessionState.RECOVERING, "recovery started")
        self._transition(SessionState.SAFE, "recovery completed in safe state")

    def close(self) -> None:
        if self._state is SessionState.CLOSED:
            return
        self._transition(SessionState.CLOSED, "session closed")

    def events(self) -> tuple[RecoveryEvent, ...]:
        return tuple(self._events)

    def _transition(self, state: SessionState, reason: str) -> None:
        self._state = state
        self._events.append(RecoveryEvent(state, reason))
