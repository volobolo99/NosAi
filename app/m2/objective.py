from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from app.m1.core.types import Action, State, Prediction


@dataclass(frozen=True)
class PlannerObjective:
    """Single goal-aware utility contract shared by all planning layers.

    The objective combines predicted reward with risk, uncertainty, goal
    progress, completion value and time cost.  Goal definitions remain
    domain-agnostic and are read from ``Goal.constraints``.
    """
    reward_weight: float = 1.0
    risk_weight: float = 0.10
    uncertainty_weight: float = 0.15
    progress_weight: float = 1.0
    completion_weight: float = 1.0
    time_cost_weight: float = 0.0
    terminal_bonus_weight: float = 0.0

    def action_risk(self, action: Action) -> float:
        p = action.parameters or {}
        risk = float(p.get("risk", 0.0) or 0.0)
        self_damage = max(0.0, float(p.get("self_damage", 0.0) or 0.0))
        return max(0.0, min(1.0, risk + self_damage / 100.0))

    @staticmethod
    def _feature(state: State, key: Any) -> float | None:
        features = state.features
        try:
            if isinstance(features, dict):
                value = features.get(key)
            else:
                value = features[key]
            return float(value) if value is not None else None
        except (KeyError, IndexError, TypeError, ValueError):
            return None

    def goal_progress(self, state: State, goal: Any | None) -> float:
        """Return normalized [0,1] progress from a goal's target_features.

        ``Goal.constraints`` supports ``target_features`` as a mapping from
        feature key/index to target value and optional ``feature_tolerances``.
        Missing targets deliberately produce zero progress rather than making
        an unsupported assumption about the domain.
        """
        if goal is None:
            return 0.0
        constraints = getattr(goal, "constraints", {}) or {}
        targets = constraints.get("target_features")
        if not isinstance(targets, dict) or not targets:
            return 0.0
        tolerances = constraints.get("feature_tolerances", {}) or {}
        values = []
        for key, target in targets.items():
            current = self._feature(state, key)
            if current is None:
                values.append(0.0)
                continue
            target = float(target)
            tolerance = max(0.0, float(tolerances.get(key, 0.0) or 0.0))
            distance = abs(current - target)
            scale = max(abs(target), tolerance, 1.0)
            values.append(max(0.0, 1.0 - distance / scale))
        return sum(values) / len(values)

    def goal_completed(self, state: State, prediction: Prediction, goal: Any | None) -> bool:
        if goal is None:
            return False
        constraints = getattr(goal, "constraints", {}) or {}
        if constraints.get("require_terminal", False) and prediction.done_probability >= 0.5:
            return True
        targets = constraints.get("target_features")
        if not isinstance(targets, dict) or not targets:
            return prediction.done_probability >= 0.999 if constraints.get("terminal_goal", False) else False
        tolerance = constraints.get("feature_tolerances", {}) or {}
        for key, target in targets.items():
            current = self._feature(prediction.next_state, key)
            if current is None or abs(current - float(target)) > float(tolerance.get(key, 0.0) or 0.0):
                return False
        return True

    def time_cost(self, goal: Any | None, elapsed_steps: int) -> float:
        if goal is None:
            return 0.0
        constraints = getattr(goal, "constraints", {}) or {}
        per_step = max(0.0, float(constraints.get("step_cost", 1.0) or 0.0))
        deadline = getattr(goal, "deadline_seconds", None)
        if deadline is None:
            deadline = constraints.get("deadline_steps")
        if deadline is not None and elapsed_steps > float(deadline):
            return per_step * elapsed_steps + (elapsed_steps - float(deadline))
        return per_step * elapsed_steps

    def utility(self, prediction: Prediction, *, uncertainty: float = 0.0,
                action_risk: float = 0.0, progress_delta: float = 0.0,
                completed: bool = False, time_cost: float = 0.0) -> float:
        terminal = max(0.0, min(1.0, prediction.done_probability))
        return (
            self.reward_weight * float(prediction.reward)
            - self.risk_weight * max(0.0, float(action_risk))
            - self.uncertainty_weight * max(0.0, float(uncertainty))
            + self.progress_weight * float(progress_delta)
            + self.completion_weight * (1.0 if completed else 0.0)
            + self.terminal_bonus_weight * terminal
            - self.time_cost_weight * max(0.0, float(time_cost))
        )

    def trajectory_step_utility(self, state: State, action: Action,
                                prediction: Prediction, uncertainty: float,
                                *, goal: Any | None = None,
                                elapsed_steps: int = 1) -> float:
        before = self.goal_progress(state, goal)
        after = self.goal_progress(prediction.next_state, goal)
        return self.utility(
            prediction,
            uncertainty=uncertainty,
            action_risk=self.action_risk(action),
            progress_delta=after - before,
            completed=self.goal_completed(state, prediction, goal),
            time_cost=self.time_cost(goal, elapsed_steps),
        )
