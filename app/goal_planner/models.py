
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class Goal:
    id: str
    kind: str
    description: str
    priority: float = 1.0
    deadline_seconds: float | None = None
    constraints: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class SubGoal:
    id: str
    parent_id: str
    kind: str
    description: str
    priority: float = 1.0
    dependencies: tuple[str, ...] = ()

@dataclass(frozen=True)
class GoalPlan:
    goal_id: str
    ordered_subgoals: tuple[SubGoal, ...]
