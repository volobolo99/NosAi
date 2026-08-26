"""Bridge minimap path candidates into goal planning and replay memory.

The bridge is proposal-only: it records navigation candidates and never executes
an action. This keeps navigation useful to the strategic brain without crossing
the runtime safety boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from app.ai.replay_buffer import ReplayBuffer, Transition
from app.client.minimap_navigation import GridPoint, MinimapPathPlanner, PathPlan
from app.client.multi_entity import MinimapObservation


@dataclass(frozen=True)
class NavigationGoal:
    goal: GridPoint
    reason: str = "strategic_goal"


class NavigationMemoryBridge:
    """Create deterministic navigation proposals and store them for replay."""

    def __init__(
        self,
        planner: MinimapPathPlanner | None = None,
        replay: ReplayBuffer | None = None,
    ) -> None:
        self.planner = planner or MinimapPathPlanner()
        self.replay = replay or ReplayBuffer(capacity=10_000)

    def propose(
        self,
        minimap: MinimapObservation,
        start: GridPoint,
        goal: NavigationGoal,
        blocked: set[GridPoint] | None = None,
        state: Mapping[str, Any] | None = None,
    ) -> PathPlan | None:
        plan = self.planner.plan(minimap, start, goal.goal, blocked)
        if plan is None:
            return None
        current = dict(state or {})
        current["navigation"] = plan.to_dict()
        next_state = dict(current)
        next_state["navigation_goal"] = {
            "x": goal.goal.x,
            "y": goal.goal.y,
            "reason": goal.reason,
        }
        self.replay.add(
            Transition(
                state=current,
                action="propose_move",
                reward=-plan.distance,
                next_state=next_state,
                info={"source": plan.source, "observation_only": True},
            )
        )
        return plan

    def latest(self) -> list[Transition]:
        return self.replay.recent(1)
