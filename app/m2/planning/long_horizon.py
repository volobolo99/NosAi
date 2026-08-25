from __future__ import annotations
from app.m1.core.types import Action, State

class LongHorizonPlanner:
    """Receding-horizon planner: plan in chunks and re-plan after each chunk."""
    def __init__(self, base_planner, chunk_size: int = 3):
        self.base=base_planner; self.chunk_size=max(1, chunk_size)

    def plan(self, state: State, actions: list[Action], total_horizon: int = 12, simulations: int = 128):
        current=state; result=[]; remaining=total_horizon
        while remaining>0:
            chunk=min(self.chunk_size, remaining)
            plan=self.base.plan(current, actions, simulations=max(1, simulations//max(1,total_horizon//chunk)), horizon=chunk)
            if not plan.actions: break
            result.extend(plan.actions[:chunk])
            traj=self.base.imagination.rollout(current, plan.actions[:chunk])
            if not traj.steps: break
            current=traj.steps[-1].prediction.next_state
            remaining-=len(plan.actions[:chunk])
        return tuple(result)
