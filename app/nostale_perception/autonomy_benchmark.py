"""Deterministic autonomy benchmark for the simulated NosAi loop."""
from __future__ import annotations

from dataclasses import dataclass

from .autonomy import SkillRequest
from .autonomy_cycle import AutonomyCycleResult, run_simulated_cycle
from .game_state import GameState
from .simulated_executor import SimulatedSkillExecutor, SimulationRule
from .skill_ledger import SkillLedger, SkillRecord


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    skill: str
    confidence: float
    expected_success: bool


@dataclass(frozen=True)
class AutonomyBenchmarkReport:
    cases: int
    accepted: int
    executed: int
    successful: int
    expected_successes: int
    correct_outcomes: int
    interventions: int
    skill_verification_count: int

    @property
    def execution_rate(self) -> float:
        return self.executed / self.cases if self.cases else 0.0

    @property
    def success_rate(self) -> float:
        return self.successful / self.executed if self.executed else 0.0

    @property
    def outcome_accuracy(self) -> float:
        return self.correct_outcomes / self.cases if self.cases else 0.0

    @property
    def intervention_rate(self) -> float:
        return self.interventions / self.cases if self.cases else 0.0


def run_benchmark(cases: list[BenchmarkCase]) -> tuple[AutonomyBenchmarkReport, list[AutonomyCycleResult]]:
    ledger = SkillLedger()
    skills = sorted({case.skill for case in cases})
    for skill in skills:
        ledger.upsert(SkillRecord(skill, "sim-v1"))

    rules = [SimulationRule(case.skill, case.expected_success) for case in cases]
    executor = SimulatedSkillExecutor(rules)
    results: list[AutonomyCycleResult] = []

    for case in cases:
        result = run_simulated_cycle(
            GameState.empty(),
            SkillRequest(case.skill, case.confidence, f"benchmark:{case.name}"),
            executor,
            ledger,
        )
        results.append(result)

    accepted = sum(result.accepted for result in results)
    executed = sum(result.executed for result in results)
    successful = sum(result.success is True for result in results)
    expected_successes = sum(case.expected_success for case in cases)
    correct_outcomes = sum(
        result.success is not None and result.success == case.expected_success
        for result, case in zip(results, cases)
    )
    interventions = sum(not result.accepted or not result.executed for result in results)
    verified = sum(record.verified for record in ledger.skills.values())
    return AutonomyBenchmarkReport(
        len(cases), accepted, executed, successful, expected_successes,
        correct_outcomes, interventions, verified,
    ), results


def default_cases() -> list[BenchmarkCase]:
    return [
        BenchmarkCase("navigation-success", "move_to_target", 0.90, True),
        BenchmarkCase("observation-success", "observe_area", 0.92, True),
        BenchmarkCase("controlled-failure", "recover_position", 0.86, False),
        BenchmarkCase("navigation-repeat", "move_to_target", 0.91, True),
        BenchmarkCase("observation-repeat", "observe_area", 0.93, True),
        BenchmarkCase("recovery-success", "recover_position", 0.88, True),
    ]
