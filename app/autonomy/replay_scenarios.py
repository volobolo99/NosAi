"""Extract deterministic benchmark scenarios from normalized replay observations.

This module intentionally accepts normalized observation dictionaries rather than
raw network bytes. Decoding remains owned by the NetworkObservation/decoder layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Any

from app.nostale_perception.game_state import GameState
from app.nostale_perception.network_decoder import DecodedObservation
from app.nostale_perception.state_invariants import validate_game_state
from .planner import Goal
from .nostale_scenarios import ScenarioKind


@dataclass(frozen=True)
class ReplayObservation:
    sequence: int
    timestamp: float
    kind: str
    payload: Mapping[str, Any]
    confidence: float = 1.0
    source: str = "replay"


@dataclass(frozen=True)
class GoldenScenario:
    scenario_id: str
    source_replay: str
    start_sequence: int
    end_sequence: int
    kind: ScenarioKind
    goal: Goal
    state: GameState
    valid: bool
    expected_block: bool


class ReplayScenarioExtractor:
    """Builds a golden fixture from a bounded replay window."""

    def __init__(self, replay_id: str) -> None:
        self.replay_id = replay_id

    def build_state(self, observations: Iterable[ReplayObservation]) -> GameState:
        state = GameState.empty()
        for observation in sorted(observations, key=lambda item: item.sequence):
            state.apply(DecodedObservation(
                packet_id=f"replay:{self.replay_id}:{observation.sequence}",
                message_type=observation.kind,
                payload=dict(observation.payload),
                confidence=observation.confidence,
                source=observation.source,
            ))
        return state

    def extract(
        self,
        observations: Iterable[ReplayObservation],
        *,
        scenario_id: str,
        kind: ScenarioKind,
        goal: Goal,
    ) -> GoldenScenario:
        items = tuple(observations)
        if not items:
            raise ValueError("cannot extract a scenario from an empty replay window")
        state = self.build_state(items)
        valid = validate_game_state(state).valid
        return GoldenScenario(
            scenario_id=scenario_id,
            source_replay=self.replay_id,
            start_sequence=min(item.sequence for item in items),
            end_sequence=max(item.sequence for item in items),
            kind=kind,
            goal=goal,
            state=state,
            valid=valid,
            expected_block=not valid,
        )
