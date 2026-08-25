from __future__ import annotations
from app.m1.core.types import Action, State
from .imagination import ImaginationEngine
from .types import CounterfactualResult

class CounterfactualEngine:
    """Evaluate an intervention against a baseline through the learned World Model."""
    def __init__(self, imagination: ImaginationEngine): self.imagination=imagination
    def compare(self, state: State, baseline: list[Action], intervention: list[Action]) -> CounterfactualResult:
        b=self.imagination.rollout(state, baseline); i=self.imagination.rollout(state, intervention)
        delta=i.discounted_return-b.discounted_return
        risk_i=i.terminal_probability; risk_b=b.terminal_probability
        confidence=1.0/(1.0+i.uncertainty+b.uncertainty)
        return CounterfactualResult(b,i,delta,risk_i-risk_b,confidence)
