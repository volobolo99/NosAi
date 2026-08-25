from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable, Sequence

try:
    from app.goal_planner.models import Goal
except Exception:  # pragma: no cover - keeps the module independently importable
    Goal = object  # type: ignore[misc,assignment]


@dataclass(frozen=True)
class SubGoal:
    id: str
    description: str
    prerequisites: tuple[str, ...] = ()
    priority: float = 0.0
    kind: str = "TASK"
    parent_id: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class TaskGraph:
    nodes: dict[str, SubGoal] = field(default_factory=dict)

    def add(self, goal: SubGoal) -> None:
        if goal.id in self.nodes:
            raise ValueError(f"duplicate sub-goal id: {goal.id}")
        if any(dep == goal.id for dep in goal.prerequisites):
            raise ValueError("a sub-goal cannot depend on itself")
        self.nodes[goal.id] = goal

    def validate(self) -> None:
        for node in self.nodes.values():
            missing = [dep for dep in node.prerequisites if dep not in self.nodes]
            if missing:
                raise ValueError(f"missing prerequisites for {node.id}: {missing}")
        # Cycle detection keeps the graph executable rather than merely representational.
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node_id: str) -> None:
            if node_id in visiting:
                raise ValueError("cyclic task graph")
            if node_id in visited:
                return
            visiting.add(node_id)
            for dep in self.nodes[node_id].prerequisites:
                visit(dep)
            visiting.remove(node_id)
            visited.add(node_id)

        for node_id in self.nodes:
            visit(node_id)

    def ready(self, completed: set[str]) -> list[SubGoal]:
        return sorted(
            (g for g in self.nodes.values()
             if g.id not in completed and all(p in completed for p in g.prerequisites)),
            key=lambda g: (-g.priority, g.id),
        )


class GoalDecomposer:
    """Goal decomposition with validation, constraints and dependency-aware metadata.

    The legacy ``decompose(goal, parts)`` API remains supported.  The 2.0 API accepts
    a Goal object and derives a deterministic plan from the goal kind/constraints.
    """

    TEMPLATES: dict[str, tuple[str, ...]] = {
        "EXP": ("CHECK_RESOURCES", "SELECT_AREA", "TRAVEL", "FARM", "RECOVER"),
        "ITEM": ("IDENTIFY_ITEM", "CHECK_SOURCES", "SELECT_SOURCE", "ACQUIRE"),
        "QUEST": ("READ_OBJECTIVE", "LOCATE_TARGET", "TRAVEL", "COMPLETE"),
        "PVM": ("ASSESS_TARGET", "PREPARE", "ENGAGE", "LOOT", "RECOVER"),
        "PVP": ("ASSESS_OPPONENT", "PREPARE", "ENGAGE", "ADAPT", "RECOVER"),
        "UPGRADE": ("CHECK_REQUIREMENTS", "ACQUIRE_MATERIALS", "UPGRADE", "VERIFY"),
    }

    def decompose(
        self,
        goal: str | Goal,
        parts: Iterable[str] | None = None,
    ) -> TaskGraph:
        if parts is not None:
            goal_id = goal.id if hasattr(goal, "id") else str(goal)
            priority = float(getattr(goal, "priority", 0.0))
            descriptions = list(parts)
            kinds = ["TASK"] * len(descriptions)
            metadata = {}
            description = str(goal_id)
        else:
            if not hasattr(goal, "id") or not hasattr(goal, "kind"):
                raise TypeError("GoalDecomposer 2.0 requires a Goal or legacy (goal, parts) input")
            goal_id = str(goal.id)
            priority = float(goal.priority)
            kinds = list(self.TEMPLATES.get(goal.kind, ("ANALYZE", "ACT", "VERIFY")))
            descriptions = [f"{kind} for {goal.description}" for kind in kinds]
            metadata = dict(goal.constraints)
            description = goal.description

        if not descriptions:
            raise ValueError("a goal must contain at least one sub-goal")

        graph = TaskGraph()
        previous: str | None = None
        for index, (kind, text) in enumerate(zip(kinds, descriptions), start=1):
            sid = f"{goal_id}.{index}" if parts is not None else f"{goal_id}:sub:{index-1}"
            node_meta = dict(metadata)
            node_meta.update({"goal_description": description, "step": index, "total_steps": len(descriptions)})
            graph.add(SubGoal(
                id=sid,
                description=text,
                prerequisites=(previous,) if previous else (),
                priority=priority + (len(descriptions) - index) * 1e-3,
                kind=kind,
                parent_id=goal_id,
                metadata=node_meta,
            ))
            previous = sid
        graph.validate()
        return graph


class HierarchicalPlanner:
    def __init__(self, graph: TaskGraph):
        graph.validate()
        self.graph = graph

    def next_subgoal(self, completed: set[str]) -> SubGoal | None:
        ready = self.graph.ready(completed)
        return ready[0] if ready else None

    def replan(self, completed: set[str], invalidated: set[str]) -> list[SubGoal]:
        remaining = set(self.graph.nodes) - completed - invalidated
        return sorted(
            (self.graph.nodes[x] for x in remaining
             if all(p in completed for p in self.graph.nodes[x].prerequisites)),
            key=lambda g: (-g.priority, g.id),
        )
