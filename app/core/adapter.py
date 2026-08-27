"""Game-agnostic adapter interfaces.

Adapters translate an external game/runtime into stable core observations and
capabilities. The core must not depend on game-specific APIs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class WorldObservation:
    """Normalized observation exposed by a game adapter."""
    state: Mapping[str, Any]
    source: str
    confidence: float = 0.0
    timestamp: str | None = None


class GameAdapter(Protocol):
    """Minimal boundary required by the generic AI core."""

    adapter_id: str
    game_id: str

    def observe(self) -> WorldObservation:
        """Return a read-only normalized observation."""
        ...

    def capabilities(self) -> Mapping[str, bool]:
        """Describe supported operations without executing them."""
        ...
