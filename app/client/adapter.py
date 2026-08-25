"""Strict, transport-neutral contract for the real game-client integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class ClientState:
    """Minimum state contract returned by a connected client."""

    tick: int
    payload: dict[str, Any]


@runtime_checkable
class ClientAdapter(Protocol):
    """Interface required by NosAi before a live client can be used.

    Implementations own the transport details. The runtime only relies on these
    methods and never assumes a specific client protocol, process layout, or
    transport mechanism.
    """

    def check_connection(self) -> bool:
        """Return True only when the target client is reachable and usable."""

    def read_state(self) -> ClientState:
        """Return a complete, normalized client state snapshot."""

    def validate_action(self, action: Any) -> bool:
        """Validate an action without executing it in the game client."""

    def close(self) -> None:
        """Release transport resources; must be safe to call during shutdown."""


def validate_adapter(adapter: Any) -> None:
    """Fail fast with a precise diagnostic when an adapter is incomplete."""

    required = ("check_connection", "read_state", "validate_action", "close")
    missing = [name for name in required if not callable(getattr(adapter, name, None))]
    if missing:
        raise TypeError(f"client adapter missing required methods: {', '.join(missing)}")
