"""Episodic and semantic-memory contracts for v5.

The module intentionally stores structured records rather than forcing every
memory into vector embeddings. Retrieval can later be backed by SQLite, a
vector index or another repository without changing the cognitive core.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Iterable, Mapping


@dataclass(frozen=True, slots=True)
class Episode:
    episode_id: str
    state_fingerprint: str
    goal: str
    action_id: str
    outcome: str
    reward: float
    metadata: Mapping[str, object] = field(default_factory=dict)
    created_at: float = field(default_factory=time)


@dataclass(frozen=True, slots=True)
class KnowledgeRecord:
    record_id: str
    kind: str
    content: str
    confidence: float = 0.5
    source: str = "unknown"
    evidence_count: int = 0
    version: int = 1

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.evidence_count < 0:
            raise ValueError("evidence_count cannot be negative")


class EpisodicMemory:
    """Bounded in-process memory suitable for tests and replay mode."""

    def __init__(self, max_episodes: int = 10_000) -> None:
        if max_episodes <= 0:
            raise ValueError("max_episodes must be positive")
        self._max_episodes = max_episodes
        self._episodes: list[Episode] = []

    def append(self, episode: Episode) -> None:
        self._episodes.append(episode)
        if len(self._episodes) > self._max_episodes:
            del self._episodes[: len(self._episodes) - self._max_episodes]

    def recent(self, limit: int = 20) -> tuple[Episode, ...]:
        if limit <= 0:
            return ()
        return tuple(self._episodes[-limit:])

    def by_action(self, action_id: str) -> tuple[Episode, ...]:
        return tuple(e for e in self._episodes if e.action_id == action_id)

    def summarize_action(self, action_id: str) -> Mapping[str, float]:
        rows = self.by_action(action_id)
        if not rows:
            return {"count": 0.0, "mean_reward": 0.0, "success_rate": 0.0}
        successes = sum(e.outcome == "success" for e in rows)
        return {
            "count": float(len(rows)),
            "mean_reward": sum(e.reward for e in rows) / len(rows),
            "success_rate": successes / len(rows),
        }

    def iter_all(self) -> Iterable[Episode]:
        return tuple(self._episodes)
