"""Small deterministic harness for evaluating autonomous policy decisions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .game_state import GameState
from .shadow_mode import ShadowDecision, ShadowExecutor


@dataclass(frozen=True)
class EvaluationSummary:
    cases: int
    successful: int
    interventions: int

    @property
    def success_rate(self) -> float:
        return self.successful / self.cases if self.cases else 0.0

    @property
    def intervention_rate(self) -> float:
        return self.interventions / self.cases if self.cases else 0.0


def evaluate_shadow_cases(cases: Iterable[tuple[GameState, bool]], policy: Callable[[GameState], ShadowDecision]) -> EvaluationSummary:
    executor = ShadowExecutor(policy)
    total = successful = interventions = 0
    for state, expected_success in cases:
        decision = executor.evaluate(state)
        total += 1
        successful += int(decision.skill != "noop" and expected_success)
    return EvaluationSummary(total, successful, interventions)
