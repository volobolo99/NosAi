from __future__ import annotations

from dataclasses import replace
import random
from statistics import median
from typing import Iterable

from .models import CharacterSnapshot, PlanResult, ProgressionPlan

class ProgressionSimulator:
    """Small dependency-free Monte Carlo model; it never touches the game client."""

    def __init__(self, seed: int = 42, simulations: int = 256) -> None:
        if simulations < 1: raise ValueError("simulations must be positive")
        self.seed, self.simulations = seed, simulations

    def evaluate(self, snapshot: CharacterSnapshot, plans: Iterable[ProgressionPlan], *, weights: dict[str, float] | None = None) -> tuple[PlanResult, ...]:
        if snapshot.validate(): raise ValueError("invalid CharacterSnapshot")
        w = {"progress": 1.0, "time": 0.15, "cost": 0.1, "risk": 1.0, **(weights or {})}
        results: list[PlanResult] = []
        for plan in plans:
            if plan.policy_status not in {"PASS", "CONDITIONAL"}:
                results.append(PlanResult(plan.plan_id, 0.0, 0.0, plan.expected_time_s, plan.expected_time_s, plan.expected_time_s, plan.resource_cost, plan.risk, 1.0, float("-inf"), "BLOCKED_BY_POLICY", ("policy",)))
                continue
            rng = random.Random(self.seed ^ hash(plan.plan_id))
            times = []
            successes = 0
            progress = []
            for _ in range(self.simulations):
                risk = max(0.0, min(1.0, plan.risk))
                success = rng.random() >= risk
                successes += int(success)
                progress.append(plan.expected_progress if success else plan.expected_progress * 0.25)
                times.append(max(0.01, rng.gauss(plan.expected_time_s, max(0.01, plan.expected_time_s * (0.05 + risk * 0.15)))))
            expected_progress = sum(progress) / len(progress)
            expected_time = sum(times) / len(times)
            p_success = successes / self.simulations
            utility = expected_progress * w["progress"] - expected_time / 3600.0 * w["time"] - plan.resource_cost * w["cost"] - plan.risk * w["risk"]
            results.append(PlanResult(plan.plan_id, expected_progress, p_success, expected_time, median(times), sorted(times)[max(0, int(len(times) * .9) - 1)], plan.resource_cost, plan.risk, max(0.0, min(1.0, snapshot.confidence)), utility, "RECOMMENDED" if p_success >= .8 else "CONDITIONAL", ("seeded_monte_carlo",)))
        return tuple(sorted(results, key=lambda x: x.utility, reverse=True))
