from __future__ import annotations
import math
import random
from dataclasses import dataclass
from app.m1.core.types import Action, State, Prediction
from app.m2.objective import PlannerObjective
from app.m2.types import CandidateScore

@dataclass
class _Node:
    state: State
    parent: "_Node | None" = None
    action: Action | None = None
    prior: float = 1.0
    visits: int = 0
    value_sum: float = 0.0
    risk_sum: float = 0.0
    uncertainty_sum: float = 0.0
    children: list["_Node"] | None = None
    terminal: bool = False
    prediction: Prediction | None = None

    def __post_init__(self):
        if self.children is None:
            self.children = []

    @property
    def value(self):
        return self.value_sum / self.visits if self.visits else 0.0


class UncertaintyMCTS:
    """Model-predictive MCTS with uncertainty-aware exploration and risk penalty."""

    def __init__(self, world_model, rng_seed: int = 42, exploration: float = 1.4,
                 uncertainty_penalty: float = 0.15, risk_penalty: float = 0.1,
                 objective: PlannerObjective | None = None):
        self.world_model = world_model
        self.rng = random.Random(rng_seed)
        self.exploration = exploration
        self.uncertainty_penalty = uncertainty_penalty
        self.risk_penalty = risk_penalty
        self.objective = objective or PlannerObjective(
            risk_weight=risk_penalty, uncertainty_weight=uncertainty_penalty
        )

    def search(self, state: State, actions: list[Action], simulations: int = 128,
               horizon: int = 5, value_fn=None, goal=None) -> tuple[Action, tuple[CandidateScore, ...]]:
        if not actions:
            raise ValueError("at least one action is required")
        if simulations < 1 or horizon < 1:
            raise ValueError("simulations and horizon must be positive")
        root = _Node(state)
        for _ in range(simulations):
            node = root
            path = [node]
            depth = 0
            while node.children and depth < horizon and not node.terminal:
                node = self._select(node)
                path.append(node)
                depth += 1
            if depth < horizon and not node.terminal:
                self._expand(node, actions)
                if node.children:
                    node = self.rng.choice(node.children)
                    path.append(node)
                    depth += 1
            value, risk, uncertainty = self._evaluate_path(path, horizon, value_fn, goal)
            self._backup(path, value, risk, uncertainty)
        best = max(root.children or [], key=lambda n: n.visits)
        scores = tuple(
            CandidateScore(
                n.action,
                n.value,
                n.risk_sum / max(n.visits, 1),
                n.uncertainty_sum / max(n.visits, 1),
                n.visits,
            )
            for n in sorted(root.children, key=lambda n: n.visits, reverse=True)
        )
        return best.action, scores

    def _expand(self, node, actions):
        if node.children:
            return
        for action in actions:
            prediction = self.world_model.predict(node.state, action)
            node.children.append(
                _Node(
                    prediction.next_state,
                    node,
                    action,
                    prior=1.0,
                    terminal=prediction.done_probability >= .999,
                    prediction=prediction,
                )
            )

    def _select(self, node):
        return max(
            node.children,
            key=lambda c: c.value
            + self.exploration * c.prior * math.sqrt(
                math.log(max(node.visits, 1) + 1) / (c.visits + 1)
            ),
        )

    def _evaluate_path(self, path, horizon, value_fn, goal=None):
        reward = risk = uncertainty = 0.0
        discount = 1.0
        for node in path[1:]:
            p = node.prediction
            if p is None:
                p = self.world_model.predict(node.parent.state, node.action)
                node.prediction = p
            step_uncertainty = 0.0
            try:
                u = self.world_model.uncertainty(node.parent.state, node.action)
                step_uncertainty = max(0.0, u.epistemic + u.aleatoric + u.ood + u.shift)
            except AttributeError:
                step_uncertainty = 0.0
            uncertainty += discount * step_uncertainty
            action_risk = self.objective.action_risk(node.action)
            # Environment-exposed action risk is aligned with terminal/model risk
            # instead of being ignored by MCTS.
            risk += discount * max(action_risk, max(0.0, p.done_probability))
            reward += discount * self.objective.trajectory_step_utility(
                node.parent.state, node.action, p, step_uncertainty,
                goal=goal, elapsed_steps=len(path) - 1
            )
            discount *= .99
        if value_fn and path:
            reward += discount * float(value_fn(path[-1].state))
        return reward - self.uncertainty_penalty * uncertainty - self.risk_penalty * risk, risk, uncertainty

    @staticmethod
    def _backup(path, value, risk, uncertainty):
        for node in path:
            node.visits += 1
            node.value_sum += value
            node.risk_sum += risk
            node.uncertainty_sum += uncertainty
