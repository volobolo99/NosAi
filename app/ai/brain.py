"""Provider-neutral strategic brain for NosAi.

The brain is deliberately split into four concerns:
- perception/state features (already supplied by adapters),
- episodic memory/replay,
- deterministic safety/strategy priors,
- action scoring with confidence and explanations.

It does not control the real client. A future policy learner can consume the
same BrainDecision contract without changing the safety boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import time
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class BrainObservation:
    """Normalized snapshot of the game state used by the strategic layer."""

    values: Mapping[str, float]
    tags: frozenset[str] = frozenset()
    timestamp: float = field(default_factory=time.time)

    def get(self, key: str, default: float = 0.0) -> float:
        value = self.values.get(key, default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default


@dataclass(frozen=True)
class CandidateAction:
    action_type: str
    score: float
    reason: str
    risk: float = 0.0
    urgency: float = 0.0


@dataclass(frozen=True)
class BrainDecision:
    action_type: str
    confidence: float
    candidates: tuple[CandidateAction, ...]
    reasons: tuple[str, ...]
    memory_hits: int = 0
    safe_fallback: bool = False


class EpisodicMemory:
    """Small bounded memory of successful/failed transitions.

    This is intentionally simple and serializable. It can later be replaced by
    a vector database or an offline learner without changing BrainDecision.
    """

    def __init__(self, capacity: int = 10_000) -> None:
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._items: list[dict[str, Any]] = []

    def remember(self, state: Mapping[str, Any], action: str, reward: float, outcome: str) -> None:
        self._items.append(
            {
                "state": dict(state),
                "action": action,
                "reward": float(reward),
                "outcome": outcome,
                "timestamp": time.time(),
            }
        )
        if len(self._items) > self.capacity:
            del self._items[: len(self._items) - self.capacity]

    def similar(self, observation: BrainObservation, limit: int = 5) -> list[dict[str, Any]]:
        scored: list[tuple[float, dict[str, Any]]] = []
        for item in self._items:
            state = item["state"]
            keys = set(observation.values) & set(state)
            if not keys:
                continue
            distance = 0.0
            for key in keys:
                try:
                    a = observation.get(key)
                    b = float(state[key])
                except (TypeError, ValueError):
                    continue
                distance += (a - b) ** 2
            similarity = 1.0 / (1.0 + math.sqrt(distance))
            scored.append((similarity, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:limit]]

    def __len__(self) -> int:
        return len(self._items)


class NosAiBrain:
    """Hierarchical decision layer: safety -> objective -> learned evidence."""

    def __init__(self, memory: EpisodicMemory | None = None) -> None:
        self.memory = memory or EpisodicMemory()

    def decide(
        self,
        observation: BrainObservation,
        actions: Sequence[str] = ("attack", "move", "heal", "retreat", "wait"),
    ) -> BrainDecision:
        values = observation.values
        hp = max(0.0, min(1.0, observation.get("hp_ratio", 1.0)))
        mp = max(0.0, min(1.0, observation.get("mp_ratio", 1.0)))
        distance = max(0.0, observation.get("target_distance", 999.0))
        resistance = max(0.0, observation.get("target_resistance", 0.0))
        time_left = max(0.0, observation.get("time_left_s", 9999.0))
        raid_lives = observation.get("raid_lives", 99.0)
        objective = str(values.get("objective", "unknown"))

        scored: list[CandidateAction] = []
        reasons: list[str] = []

        danger = max(0.0, 1.0 - hp) + (1.0 if raid_lives <= 1 else 0.0)
        if hp < 0.25 or raid_lives <= 1 and hp < 0.55:
            reasons.append("survival priority")
            if "retreat" in actions:
                scored.append(CandidateAction("retreat", 4.0 + danger, "high survival risk", danger, 1.0))
            if "heal" in actions:
                scored.append(CandidateAction("heal", 3.5 + danger, "low HP", danger, 0.9))

        if resistance >= 1.0:
            reasons.append("target resistance at/above 100%")
            if "move" in actions:
                scored.append(CandidateAction("move", 2.8, "seek a better target/position", 0.2, 0.7))
        elif "attack" in actions:
            attack_score = 2.0 + (1.0 if distance < 10 else 0.0)
            if objective in {"kill_all", "target_elimination", "raid"}:
                attack_score += 1.0
            if time_left < 30:
                attack_score += 0.7
                reasons.append("time pressure")
            scored.append(CandidateAction("attack", attack_score, "objective progress", 0.2, min(1.0, 30 / max(time_left, 1))))

        if objective in {"survival", "escort"} and "retreat" in actions:
            scored.append(CandidateAction("retreat", 1.5 + danger, "objective favors survival", danger, 0.5))

        if mp < 0.12 and "wait" in actions:
            scored.append(CandidateAction("wait", 1.2, "low MP reserve", 0.1, 0.2))

        memory_hits = self.memory.similar(observation, limit=5)
        for item in memory_hits:
            if item["action"] in actions:
                bonus = max(-1.0, min(1.5, float(item["reward"]) / 10.0))
                scored.append(
                    CandidateAction(item["action"], 0.35 + bonus, "similar past episode", 0.1, 0.2)
                )

        if not scored:
            fallback = "wait" if "wait" in actions else actions[0]
            return BrainDecision(fallback, 0.0, (), ("no safe candidate",), len(memory_hits), True)

        # Aggregate duplicate actions and retain the strongest explanation.
        aggregate: dict[str, CandidateAction] = {}
        for candidate in scored:
            previous = aggregate.get(candidate.action_type)
            if previous is None or candidate.score > previous.score:
                aggregate[candidate.action_type] = candidate
            elif previous is not None:
                aggregate[candidate.action_type] = CandidateAction(
                    candidate.action_type,
                    previous.score + candidate.score * 0.15,
                    previous.reason,
                    max(previous.risk, candidate.risk),
                    max(previous.urgency, candidate.urgency),
                )

        ranked = sorted(aggregate.values(), key=lambda item: item.score, reverse=True)
        top = ranked[0]
        margin = top.score - (ranked[1].score if len(ranked) > 1 else 0.0)
        confidence = max(0.0, min(1.0, 0.45 + margin / max(abs(top.score), 1.0) * 0.55))
        reasons.append(top.reason)
        return BrainDecision(top.action_type, confidence, tuple(ranked), tuple(dict.fromkeys(reasons)), len(memory_hits), False)
