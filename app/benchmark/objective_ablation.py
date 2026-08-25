from __future__ import annotations
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import fmean

from app.m1.core.types import Action, Prediction, State, Uncertainty
from app.m2.objective import PlannerObjective
from app.m2.planning.mcts import UncertaintyMCTS


@dataclass(frozen=True)
class ObjectiveCase:
    name: str
    reward: float
    progress: float
    risk: float
    expected_utility_reward_only: float
    expected_utility_goal_aware: float


@dataclass(frozen=True)
class ObjectiveAblationReport:
    cases: tuple[ObjectiveCase, ...]
    reward_only_goal_success: float
    goal_aware_goal_success: float
    reward_only_utility: float
    goal_aware_utility: float
    goal_aware_improves_goal_success: bool
    goal_aware_improves_utility: bool

    def to_dict(self) -> dict:
        return asdict(self)


class _GoalChoiceWorldModel:
    """Tiny deterministic model used only to validate objective alignment."""
    def __init__(self):
        self.transitions = {
            "shortcut": (0.0, 3.0, 0.8),
            "progress": (0.6, 1.0, 0.1),
        }

    def predict(self, state: State, action: Action) -> Prediction:
        progress, reward, risk = self.transitions[action.id]
        next_state = State(
            features={"progress": progress},
            timestamp=state.timestamp + 1,
            scenario_id=state.scenario_id,
            metadata={"risk": risk},
        )
        return Prediction(next_state, reward, 0.0, reward)

    def uncertainty(self, state: State, action: Action) -> Uncertainty:
        return Uncertainty(0.0, 0.0)


def _goal() -> object:
    class Goal:
        constraints = {
            "target_features": {"progress": 1.0},
            "feature_tolerances": {"progress": 0.05},
            "step_cost": 0.0,
        }
    return Goal()


def run_objective_ablation() -> ObjectiveAblationReport:
    wm = _GoalChoiceWorldModel()
    state = State(features={"progress": 0.0})
    actions = [Action("shortcut", {"risk": 0.8}), Action("progress", {"risk": 0.1})]
    goal = _goal()

    reward_only = PlannerObjective(
        reward_weight=1.0,
        risk_weight=0.0,
        uncertainty_weight=0.0,
        progress_weight=0.0,
        completion_weight=0.0,
    )
    goal_aware = PlannerObjective(
        reward_weight=1.0,
        risk_weight=1.0,
        uncertainty_weight=0.0,
        progress_weight=5.0,
        completion_weight=2.0,
    )

    cases = []
    for action in actions:
        p = wm.predict(state, action)
        cases.append(ObjectiveCase(
            action.id,
            p.reward,
            goal_aware.goal_progress(p.next_state, goal),
            goal_aware.action_risk(action),
            reward_only.trajectory_step_utility(state, action, p, 0.0, goal=goal),
            goal_aware.trajectory_step_utility(state, action, p, 0.0, goal=goal),
        ))

    reward_mcts = UncertaintyMCTS(wm, rng_seed=7, objective=reward_only)
    goal_mcts = UncertaintyMCTS(wm, rng_seed=7, objective=goal_aware)
    reward_action, _ = reward_mcts.search(state, actions, simulations=64, horizon=1, goal=None)
    goal_action, _ = goal_mcts.search(state, actions, simulations=64, horizon=1, goal=goal)

    reward_success = float(reward_action.id == "progress")
    goal_success = float(goal_action.id == "progress")
    reward_utility = max(c.expected_utility_reward_only for c in cases)
    goal_utility = max(c.expected_utility_goal_aware for c in cases)

    return ObjectiveAblationReport(
        tuple(cases), reward_success, goal_success, reward_utility, goal_utility,
        goal_success > reward_success, goal_utility > reward_utility,
    )


def save_report(path: str | Path) -> ObjectiveAblationReport:
    report = run_objective_ablation()
    Path(path).write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return report


if __name__ == "__main__":
    report = run_objective_ablation()
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
