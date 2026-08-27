"""Controlled runtime session lifecycle for G3.13."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from time import monotonic

from .recovery import RuntimeRecovery, SessionState


class SessionEvent(str, Enum):
    STARTED = "started"
    HEARTBEAT = "heartbeat"
    TIMEOUT = "timeout"
    CLOSED = "closed"


@dataclass(frozen=True)
class SessionSnapshot:
    session_id: str
    state: SessionState
    last_heartbeat: float | None
    kill_switch_engaged: bool


class RuntimeSessionManager:
    """Fail-closed lifecycle wrapper around the certified recovery machine."""

    def __init__(self, recovery: RuntimeRecovery, timeout_seconds: float = 30.0) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._recovery = recovery
        self._timeout = timeout_seconds
        self._session_id: str | None = None
        self._last_heartbeat: float | None = None
        self._events: list[SessionEvent] = []

    def start(self, session_id: str) -> SessionSnapshot:
        if not session_id.strip():
            raise ValueError("session_id must be non-empty")
        if self._session_id is not None and self._recovery.state is not SessionState.CLOSED:
            raise RuntimeError("session already active")
        self._session_id = session_id
        self._recovery.start()
        self._last_heartbeat = monotonic()
        self._events.append(SessionEvent.STARTED)
        return self.snapshot()

    def heartbeat(self, *, now: float | None = None) -> SessionSnapshot:
        if self._session_id is None or self._recovery.state is not SessionState.ACTIVE:
            raise RuntimeError("active session required")
        self._last_heartbeat = monotonic() if now is None else now
        self._events.append(SessionEvent.HEARTBEAT)
        return self.snapshot()

    def check_timeout(self, *, now: float | None = None) -> SessionSnapshot:
        if self._session_id is None or self._last_heartbeat is None:
            return self.snapshot()
        current = monotonic() if now is None else now
        if self._recovery.state is SessionState.ACTIVE and current - self._last_heartbeat > self._timeout:
            self._recovery.fault("session heartbeat timeout")
            self._events.append(SessionEvent.TIMEOUT)
        return self.snapshot()

    def close(self) -> SessionSnapshot:
        if self._session_id is None:
            return self.snapshot()
        self._recovery.close()
        self._events.append(SessionEvent.CLOSED)
        return self.snapshot()

    def snapshot(self) -> SessionSnapshot:
        return SessionSnapshot(
            self._session_id or "",
            self._recovery.state,
            self._last_heartbeat,
            self._recovery.kill_switch_engaged,
        )

    def events(self) -> tuple[SessionEvent, ...]:
        return tuple(self._events)
