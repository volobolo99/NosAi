"""Deterministic episodic-memory retrieval.

First retrieval layer: cheap, explainable and embedding-free.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from app.ai.contracts import MemoryRecord


@dataclass(frozen=True)
class MemoryMatch:
    record: MemoryRecord
    score: float
    reasons: tuple[str, ...]


class MemoryRetriever:
    """Rank experiences using exact/structured signals only."""

    def __init__(self, max_results: int = 5):
        if max_results < 1:
            raise ValueError("max_results must be >= 1")
        self.max_results = max_results

    @staticmethod
    def _score(record: MemoryRecord, *, state_fingerprint: str | None, goal_kind: str | None, action_kind: str | None) -> MemoryMatch:
        score = 0.0
        reasons: list[str] = []
        if state_fingerprint and record.state_fingerprint == state_fingerprint:
            score += 1.0
            reasons.append("same_state")
        if goal_kind and record.goal.kind == goal_kind:
            score += 0.5
            reasons.append("same_goal")
        if action_kind and record.intent.kind.value == action_kind:
            score += 0.25
            reasons.append("same_action")
        reward = float(record.reward.components.get("total", 0.0))
        score += max(-0.25, min(0.25, reward / 100.0))
        reasons.append("reward_signal")
        return MemoryMatch(record, score, tuple(reasons))

    def retrieve(self, records: Iterable[MemoryRecord], *, state_fingerprint: str | None = None, goal_kind: str | None = None, action_kind: str | None = None) -> Sequence[MemoryMatch]:
        matches = [self._score(r, state_fingerprint=state_fingerprint, goal_kind=goal_kind, action_kind=action_kind) for r in records]
        matches.sort(key=lambda m: m.score, reverse=True)
        return tuple(matches[: self.max_results])
