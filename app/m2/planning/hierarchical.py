from __future__ import annotations
from dataclasses import dataclass
from app.m1.core.types import Action, State

@dataclass(frozen=True)
class SubGoal:
    id: str
    predicate: object
    horizon: int

class HierarchicalPlanner:
    def __init__(self, low_level_planner):
        self.low_level = low_level_planner

    def plan(self, state: State, subgoals: list[SubGoal], action_space: list[Action], budget: int = 64):
        actions=[]; remaining=budget; current=state
        for goal in subgoals:
            if remaining <= 0: break
            result=self.low_level.plan(current, action_space, simulations=max(4, remaining), horizon=max(1, goal.horizon), goal=goal.predicate)
            actions.extend(result.actions)
            if result.actions:
                current=self.low_level.imagination.rollout(current, result.actions).steps[-1].prediction.next_state
            remaining=max(0, remaining-result.simulations)
        return tuple(actions)
