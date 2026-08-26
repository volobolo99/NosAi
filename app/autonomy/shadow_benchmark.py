"""Deterministic shadow benchmark for baseline-vs-AI proposals.

The benchmark evaluates proposals in simulation only; AI proposals never reach an executor.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.nostale_perception.game_state import GameState
from app.nostale_perception.simulated_executor import SimulatedSkillExecutor, SimulationRule
from .ai_planner import ShadowAIPlanner
from .planner import DeterministicPlanner, Goal
from .shadow_compare import ShadowComparator
from .shadow_ledger import ShadowLedger


@dataclass(frozen=True)
class ShadowBenchmarkReport:
    episodes: int
    agreements: int
    valid_ai: int
    allowed_ai: int
    baseline_successes: int
    baseline_failures: int
    baseline_blocked: int
    agreement_rate: float
    ai_valid_rate: float
    ai_allowed_rate: float
    baseline_success_rate: float


class ShadowBenchmark:
    def __init__(self, ai_planner: ShadowAIPlanner) -> None:
        self.ai_planner = ai_planner

    def run(self, episodes: Iterable[tuple[GameState, Goal]]) -> ShadowBenchmarkReport:
        ledger = ShadowLedger()
        comparator = ShadowComparator(self.ai_planner, ledger)
        baseline_successes = baseline_failures = baseline_blocked = 0
        count = 0

        for state, goal in episodes:
            comparison = comparator.compare(state, goal)
            count += 1
            record = comparison.record
            if record.agreement:
                pass
            if record.ai_valid:
                pass

            trace = comparison.deterministic
            if trace.selected_skill is None:
                baseline_blocked += 1
                continue

            executor = SimulatedSkillExecutor([
                SimulationRule(trace.selected_skill, True, "benchmark success")
            ])
            result = executor.execute(trace.selected_skill, state)
            if result.success:
                baseline_successes += 1
            else:
                baseline_failures += 1

        return ShadowBenchmarkReport(
            episodes=count,
            agreements=sum(r.agreement for r in ledger.records),
            valid_ai=sum(r.ai_valid for r in ledger.records),
            allowed_ai=sum(r.ai_allowed for r in ledger.records),
            baseline_successes=baseline_successes,
            baseline_failures=baseline_failures,
            baseline_blocked=baseline_blocked,
            agreement_rate=ledger.agreement_rate(),
            ai_valid_rate=ledger.valid_rate(),
            ai_allowed_rate=sum(r.ai_allowed for r in ledger.records) / count if count else 0.0,
            baseline_success_rate=baseline_successes / (baseline_successes + baseline_failures) if (baseline_successes + baseline_failures) else 0.0,
        )
