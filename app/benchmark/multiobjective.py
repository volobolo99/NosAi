from __future__ import annotations
from dataclasses import dataclass, asdict
from statistics import fmean
from typing import Iterable

@dataclass(frozen=True)
class ObjectiveWeights:
    reward: float = 1.0
    success: float = 10.0
    efficiency: float = 1.0
    risk: float = 2.0
    failure: float = 5.0

@dataclass(frozen=True)
class EpisodeOutcome:
    reward: float
    steps: int
    success: bool
    risk: float
    ood: float
    shift: float

@dataclass(frozen=True)
class ScenarioMetrics:
    scenario: str
    episodes: int
    mean_reward: float
    reward_std: float
    success_rate: float
    mean_steps: float
    mean_risk: float
    ood_rate: float
    shift_rate: float
    utility: float

@dataclass(frozen=True)
class MultiObjectiveReport:
    scenarios: tuple[ScenarioMetrics, ...]
    aggregate_utility: float
    aggregate_success: float
    aggregate_reward: float
    aggregate_risk: float
    worst_case_utility: float

    def to_dict(self) -> dict:
        return asdict(self)


def score_episode(outcome: EpisodeOutcome, weights: ObjectiveWeights, max_steps: int) -> float:
    efficiency = max(0.0, 1.0 - outcome.steps / max(1, max_steps))
    return (
        weights.reward * outcome.reward
        + weights.success * float(outcome.success)
        + weights.efficiency * efficiency
        - weights.risk * outcome.risk
        - weights.failure * float(not outcome.success)
    )


def summarize(scenario: str, outcomes: Iterable[EpisodeOutcome], weights: ObjectiveWeights, max_steps: int) -> ScenarioMetrics:
    rows = list(outcomes)
    rewards = [r.reward for r in rows]
    return ScenarioMetrics(
        scenario=scenario,
        episodes=len(rows),
        mean_reward=fmean(rewards) if rewards else 0.0,
        reward_std=(sum((x-fmean(rewards))**2 for x in rewards)/len(rewards))**0.5 if rewards else 0.0,
        success_rate=fmean(float(r.success) for r in rows) if rows else 0.0,
        mean_steps=fmean(r.steps for r in rows) if rows else 0.0,
        mean_risk=fmean(r.risk for r in rows) if rows else 0.0,
        ood_rate=fmean(float(r.ood > 0.5) for r in rows) if rows else 0.0,
        shift_rate=fmean(float(r.shift > 0.5) for r in rows) if rows else 0.0,
        utility=fmean(score_episode(r, weights, max_steps) for r in rows) if rows else 0.0,
    )


def aggregate(metrics: Iterable[ScenarioMetrics]) -> MultiObjectiveReport:
    rows = list(metrics)
    if not rows:
        return MultiObjectiveReport((), 0.0, 0.0, 0.0, 0.0, 0.0)
    return MultiObjectiveReport(
        scenarios=tuple(rows),
        aggregate_utility=fmean(r.utility for r in rows),
        aggregate_success=fmean(r.success_rate for r in rows),
        aggregate_reward=fmean(r.mean_reward for r in rows),
        aggregate_risk=fmean(r.mean_risk for r in rows),
        worst_case_utility=min(r.utility for r in rows),
    )
