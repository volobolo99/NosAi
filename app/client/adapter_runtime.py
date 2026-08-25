"""Runtime helpers for strict client-adapter integration.

The module deliberately contains no game-specific transport. It provides a
safe boundary that can be used by a real NosTale adapter once one is supplied.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.client import ClientState


@dataclass(frozen=True)
class ClientProbeResult:
    connected: bool
    state_valid: bool
    action_valid: bool
    detail: str


def probe_client(adapter: Any) -> ClientProbeResult:
    """Run a non-destructive live probe through the strict adapter contract."""
    if not bool(adapter.check_connection()):
        return ClientProbeResult(False, False, False, "connection check returned false")

    state = adapter.read_state()
    if not isinstance(state, ClientState):
        raise TypeError("client adapter read_state() must return ClientState")

    # None is the canonical dry-run action used by the adapter contract.
    action_valid = bool(adapter.validate_action(None))
    return ClientProbeResult(True, True, action_valid, "connected; state readable; dry-run validated")
