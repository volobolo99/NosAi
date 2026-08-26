from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from app.ai.brain import BrainObservation, NosAiBrain

from .evaluator import EvaluationResult, evaluate_decision
from .scenarios import default_scenarios, validate_scenarios


@dataclass(frozen=True)
class ScenarioRun:
    result: EvaluationResult
    world_state: Mapping[str, Any]


def _observation(world_state: Mapping[str, Any]) -> BrainObservation:
    numeric: dict[str, float] = {}
    for key, value in world_state.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            numeric[key] = float(value)
    return BrainObservation(values=numeric)


def run_scenario(brain: NosAiBrain, scenario: Mapping[str, Any], candidate_id: str = "nosai-brain") -> ScenarioRun:
    world = scenario["world_state"]
    actions: Sequence[str] = scenario["available_actions"]
    forbidden: Sequence[str] = scenario.get("constraints", {}).get("forbidden_actions", ())
    decision = brain.decide(_observation(world), actions=actions)
    result = evaluate_decision(
        scenario_id=str(scenario["scenario_id"]),
        candidate_id=candidate_id,
        decision=decision.action_type,
        confidence=decision.confidence,
        available_actions=actions,
        expected_decision=scenario.get("expected_decision"),
        forbidden_actions=forbidden,
    )
    return ScenarioRun(result=result, world_state=world)


def run_baseline(brain: NosAiBrain | None = None) -> tuple[ScenarioRun, ...]:
    scenarios = default_scenarios()
    errors = validate_scenarios(scenarios)
    if errors:
        raise ValueError("invalid evaluation scenarios: " + ", ".join(errors))
    active_brain = brain or NosAiBrain()
    return tuple(run_scenario(active_brain, scenario) for scenario in scenarios)
