"""Glue layer connecting NosTale strategy state to the strategic brain."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping

from app.ai.brain import BrainObservation, BrainDecision, NosAiBrain


class BrainPipeline:
    """Convert a domain state object/mapping into a stable brain decision."""

    def __init__(self, brain: NosAiBrain | None = None) -> None:
        self.brain = brain or NosAiBrain()

    def observe(self, state: Any) -> BrainObservation:
        if isinstance(state, Mapping):
            raw = dict(state)
        elif hasattr(state, "__dataclass_fields__"):
            raw = asdict(state)
        else:
            raw = {
                key: value
                for key, value in vars(state).items()
                if not key.startswith("_") and isinstance(value, (int, float, str, bool))
            }

        numeric: dict[str, float] = {}
        tags: set[str] = set()
        for key, value in raw.items():
            if isinstance(value, bool):
                numeric[key] = float(value)
            elif isinstance(value, (int, float)):
                numeric[key] = float(value)
            elif isinstance(value, str):
                if key in {"objective", "room_objective", "map", "mode"}:
                    numeric[key] = value  # type: ignore[assignment]
                    tags.add(value)
        return BrainObservation(numeric, frozenset(tags))

    def decide(self, state: Any, actions: tuple[str, ...] | None = None) -> BrainDecision:
        observation = self.observe(state)
        return self.brain.decide(observation, actions or ("attack", "move", "heal", "retreat", "wait"))
