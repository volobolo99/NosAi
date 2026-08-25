from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable

@dataclass(frozen=True)
class HorizonStep:
    action: Any
    value: float
    risk: float = 0.0
    uncertainty: float = 0.0
    depth: int = 0

@dataclass(frozen=True)
class StrategyPlan:
    steps: tuple[HorizonStep, ...]
    total_value: float
    total_risk: float
    confidence: float

class LongHorizonStrategy:
    """Deterministic receding-horizon strategy evaluator."""
    def __init__(self, discount: float = .97, risk_penalty: float = .5, uncertainty_penalty: float = .25):
        self.discount = float(discount); self.risk_penalty=float(risk_penalty); self.uncertainty_penalty=float(uncertainty_penalty)
    def evaluate(self, steps: Iterable[HorizonStep]) -> StrategyPlan:
        rows=tuple(steps)
        if not rows: return StrategyPlan((),0.0,0.0,0.0)
        value=sum((self.discount**s.depth)*(s.value-self.risk_penalty*s.risk-self.uncertainty_penalty*s.uncertainty) for s in rows)
        risk=sum(max(0.0,s.risk)*(self.discount**s.depth) for s in rows)
        conf=max(0.0,min(1.0,1.0-sum(max(0.0,s.uncertainty) for s in rows)/len(rows)))
        return StrategyPlan(rows,value,risk,conf)
    def choose(self, candidates: Iterable[Iterable[HorizonStep]]) -> StrategyPlan:
        plans=[self.evaluate(c) for c in candidates]
        if not plans: raise ValueError('no strategies')
        return max(plans,key=lambda p:(p.total_value,p.confidence,-p.total_risk))
