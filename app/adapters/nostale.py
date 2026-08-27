"""NosTale-specific adapter boundary.

This first version is intentionally observation-only. It can normalize an
already available runtime/world-state mapping without introducing direct game
execution or game-specific automation.
"""
from __future__ import annotations

from typing import Any, Mapping

from app.core.adapter import GameAdapter, WorldObservation


class NosTaleAdapter:
    adapter_id = "nostale-observation"
    game_id = "nostale"

    def __init__(self, state_provider: callable | None = None) -> None:
        self._state_provider = state_provider

    def observe(self) -> WorldObservation:
        state: Mapping[str, Any] = {}
        if self._state_provider is not None:
            candidate = self._state_provider()
            if isinstance(candidate, Mapping):
                state = dict(candidate)
        return WorldObservation(state=state, source=self.adapter_id, confidence=0.0)

    def capabilities(self) -> Mapping[str, bool]:
        return {
            "observe": True,
            "act": False,
            "trade": False,
            "purchase": False,
        }


# Structural assertion for maintainers/type-checkers.
_ADAPTER_PROTOCOL: type[GameAdapter] = NosTaleAdapter
