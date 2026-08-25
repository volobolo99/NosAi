from __future__ import annotations
from dataclasses import dataclass
from app.m1.adapters import to_m1_state, to_m1_action, to_world_action
from .adaptive import AdaptivePlanner, AdaptiveDecision


@dataclass(frozen=True)
class M4Result:
    action: object
    plan: object
    adaptation: AdaptiveDecision


class M4PlanningStack:
    """Adaptive planning facade over M3/M2 without changing their contracts."""
    def __init__(self, m3_stack, *, seed: int = 42, horizon: int = 5):
        self.m3_stack = m3_stack
        self.adaptive = AdaptivePlanner(seed=seed, max_horizon=max(2, horizon * 2))
        self.horizon = horizon

    def choose(self, world_state, world_actions, *, goal=None) -> M4Result:
        state = to_m1_state(world_state)
        actions = [to_m1_action(a) for a in world_actions]
        wm = self.m3_stack.m2_stack.m1_stack.world_model
        uncertainty = 0.0
        if actions:
            uncertainty = float(wm.uncertainty(state, actions[0]).epistemic)
        meta = self.m3_stack.meta.snapshot()
        decision = self.adaptive.decide(
            uncertainty=uncertainty,
            ood=float(state.metadata.get("ood", 0.0)) if isinstance(state.metadata, dict) else 0.0,
            shift=float(state.metadata.get("shift", 0.0)) if isinstance(state.metadata, dict) else 0.0,
            causal_confidence=max(0.0, min(1.0, meta.get("causal", 0.0))),
            memory_confidence=max(0.0, min(1.0, meta.get("memory", 0.0))),
            action_count=len(actions), horizon_hint=self.horizon,
        )
        action, plan = self.m3_stack.m2_stack.choose(
            world_state, world_actions,
            simulations=decision.simulations,
            horizon=decision.horizon,
            risk_penalty=decision.risk_penalty,
            uncertainty_penalty=decision.uncertainty_penalty,
            goal=goal,
        )
        return M4Result(action, plan, decision)
