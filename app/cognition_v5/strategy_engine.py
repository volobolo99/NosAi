"""Strategy hypotheses and evidence aggregation for NosAi v5."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .memory import EpisodicMemory
from .world_state import WorldState


@dataclass(frozen=True, slots=True)
class Strategy:
    strategy_id: str
    goal: str
    base_value: float
    risk: float = 0.0
    prerequisites: Mapping[str, object] = field(default_factory=dict)
    source: str = "unknown"
    confidence: float = 0.5


@dataclass(frozen=True, slots=True)
class StrategyScore:
    strategy_id: str
    score: float
    confidence: float
    evidence_count: int
    rationale: tuple[str, ...]


class StrategyEngine:
    """Ranks documented strategies using current state and observed evidence."""

    def __init__(self, memory: EpisodicMemory) -> None:
        self.memory = memory

    def applicable(self, strategy: Strategy, state: WorldState) -> bool:
        return all(state.get(k) == expected for k, expected in strategy.prerequisites.items())

    def score(self, strategy: Strategy, state: WorldState) -> StrategyScore:
        evidence = self.memory.summarize_action(strategy.strategy_id)
        observed = evidence["mean_reward"] if evidence["count"] else strategy.base_value
        observed_conf = evidence["success_rate"] if evidence["count"] else strategy.confidence
        # Evidence is allowed to influence a strategy, but never erase provenance.
        score = observed * max(observed_conf, 0.01) - strategy.risk
        rationale = (
            f"source={strategy.source}",
            f"evidence_count={int(evidence['count'])}",
            "observed evidence used" if evidence["count"] else "no observed evidence; source prior used",
        )
        return StrategyScore(strategy.strategy_id, score, observed_conf, int(evidence["count"]), rationale)

    def rank(self, strategies: list[Strategy], state: WorldState) -> tuple[StrategyScore, ...]:
        applicable = [s for s in strategies if self.applicable(s, state)]
        return tuple(sorted((self.score(s, state) for s in applicable), key=lambda x: x.score, reverse=True))
