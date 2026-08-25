from __future__ import annotations
from app.m1.adapters import to_m1_state, to_m1_action, to_world_action
from app.m1.integration import M1LearningStack
from .planner import M2Planner
from .objective import PlannerObjective

class M2PlanningStack:
    """Integration facade that adds M2 planning without replacing the v4.13 loop."""
    def __init__(self, m1_stack: M1LearningStack, simulations: int = 64, horizon: int = 5, seed: int = 42):
        self.m1_stack = m1_stack
        self.simulations = simulations
        self.horizon = horizon
        self.planner = M2Planner(m1_stack.world_model, seed=seed)

    def refresh_world_model(self):
        self.planner = M2Planner(self.m1_stack.world_model)

    def choose(self, world_state, world_actions, *, simulations=None, horizon=None,
               risk_penalty=None, uncertainty_penalty=None, objective: PlannerObjective | None = None, goal=None):
        state = to_m1_state(world_state)
        actions = [to_m1_action(a) for a in world_actions]
        sims = self.simulations if simulations is None else max(1, int(simulations))
        h = self.horizon if horizon is None else max(1, int(horizon))
        if any(x is not None for x in (risk_penalty, uncertainty_penalty, objective)):
            self.planner = M2Planner(
                self.m1_stack.world_model, seed=42,
                risk_penalty=0.10 if risk_penalty is None else float(risk_penalty),
                uncertainty_penalty=0.15 if uncertainty_penalty is None else float(uncertainty_penalty),
                objective=objective,
            )
        result = self.planner.plan(state, actions, simulations=sims, horizon=h, goal=goal)
        return to_world_action(result.actions[0]) if result.actions else None, result
