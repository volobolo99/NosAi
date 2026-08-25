from __future__ import annotations
from app.m1.core.types import Action, State

class LearnedActionPruner:
    """Prune actions using model-predicted value, uncertainty and safety constraints."""
    def __init__(self, world_model, max_uncertainty: float = 10.0, min_reward: float = float('-inf')):
        self.world_model = world_model
        self.max_uncertainty = max_uncertainty
        self.min_reward = min_reward

    def filter(self, state: State, actions: list[Action]) -> list[Action]:
        scored=[]
        for action in actions:
            p=self.world_model.predict(state, action)
            try: u=self.world_model.uncertainty(state, action); uncertainty=u.epistemic+u.aleatoric+u.ood+u.shift
            except AttributeError: uncertainty=0.0
            if p.reward >= self.min_reward and uncertainty <= self.max_uncertainty:
                scored.append((p.reward-uncertainty, action))
        scored.sort(key=lambda x:x[0], reverse=True)
        return [a for _,a in scored]
