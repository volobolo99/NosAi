from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable

@dataclass(frozen=True)
class Decision:
    action: Any; score: float; confidence: float; compute_budget: int; rationale: tuple[str,...]=()

class MetaDecisionLayer:
    def choose_strategy(self,*,uncertainty,risk,goal_distance):
        if risk>=.7:return 'safe'
        if uncertainty>=.7:return 'explore'
        if goal_distance>=.6:return 'long_horizon'
        return 'balanced'
    def weights(self,*,uncertainty,risk,goal_distance):
        strategy=self.choose_strategy(uncertainty=uncertainty,risk=risk,goal_distance=goal_distance)
        return {'safe':(.6,.2,.2),'explore':(.25,.5,.25),'long_horizon':(.2,.2,.6),'balanced':(.34,.33,.33)}[strategy]

class AdaptiveCompute:
    def budget(self,*,uncertainty,risk,base=32,maximum=512): return min(maximum,max(base,int(base*(1+2*max(uncertainty,risk)))))
    def schedule(self,uncertainty,risk,base=32,maximum=512): return self.budget(uncertainty=uncertainty,risk=risk,base=base,maximum=maximum)

class UnifiedPlanner:
    def __init__(self,meta=None,compute=None,learned_weights=None):
        self.meta=meta or MetaDecisionLayer();self.compute=compute or AdaptiveCompute();self.learned_weights=dict(learned_weights or {})

    def set_learned_weights(self, weights):
        self.learned_weights={str(k):float(v) for k,v in dict(weights).items()}

    def fuse(self,candidates,*,uncertainty,risk,goal_distance=0.0):
        rows=list(candidates)
        if not rows:raise ValueError('no candidates')
        strategy=self.meta.choose_strategy(uncertainty=uncertainty,risk=risk,goal_distance=goal_distance);budget=self.compute.budget(uncertainty=uncertainty,risk=risk)
        def rank(r):
            if self.learned_weights:
                return (self.learned_weights.get('score', 1.0) * float(r.get('score', 0))
                        - self.learned_weights.get('risk', 1.0) * float(r.get('risk', 0))
                        - self.learned_weights.get('uncertainty', 1.0) * float(r.get('uncertainty', 0))
                        + self.learned_weights.get('confidence', 0.0) * float(r.get('confidence', 0)))
            return float(r.get('score',0))-risk*float(r.get('risk',0))-uncertainty*float(r.get('uncertainty',0))
        best=max(rows,key=rank)
        conf=max(0,min(1,float(best.get('confidence',1))*(1-max(uncertainty,risk))))
        return Decision(best['action'],float(best.get('score',0)),conf,budget,(strategy,))
    def fuse_layers(self,*,planner_candidates,memory_candidates=(),causal_candidates=(),world_candidates=(),uncertainty=0,risk=0,goal_distance=0):
        rows=list(planner_candidates)+list(memory_candidates)+list(causal_candidates)+list(world_candidates)
        return self.fuse(rows,uncertainty=uncertainty,risk=risk,goal_distance=goal_distance)
