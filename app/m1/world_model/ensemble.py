"""Uncertainty-aware World Model ensemble."""
from __future__ import annotations
import statistics
from ..core.types import Prediction, Uncertainty
from .base import WorldModel

class WorldModelEnsemble(WorldModel):
    def __init__(self, models):
        if len(models) < 2:
            raise ValueError('at least two independent models required')
        self.models=list(models)

    def model_predictions(self,state,action):
        return [m.predict(state,action) for m in self.models]

    def predict(self,state,action):
        ps=self.model_predictions(state,action)
        rewards=[p.reward for p in ps]; vals=[p.value for p in ps]; dones=[p.done_probability for p in ps]
        # Use the first model's state representation as the canonical state type.
        return Prediction(ps[0].next_state, statistics.fmean(rewards), statistics.fmean(dones), statistics.fmean(vals))

    def disagreement(self,state,action):
        ps=self.model_predictions(state,action)
        if len(ps)<2: return 0.0
        return float(statistics.pvariance([p.reward for p in ps]))

    def state_disagreement(self,state,action):
        ps=self.model_predictions(state,action)
        vecs=[]
        for p in ps:
            x=getattr(p.next_state,'features',None)
            if x is not None: vecs.append(tuple(float(v) for v in x))
        if len(vecs)<2: return 0.0
        dims=min(map(len,vecs)); return float(sum(statistics.pvariance([v[d] for v in vecs]) for d in range(dims))/dims)

    def uncertainty(self,state,action):
        reward_d=self.disagreement(state,action); state_d=self.state_disagreement(state,action)
        epistemic=reward_d+state_d
        return Uncertainty(epistemic=epistemic,aleatoric=0.0,confidence=1/(1+epistemic))

    def rollout(self,state,actions):
        out=[]; s=state
        for a in actions:
            p=self.predict(s,a); out.append(p); s=p.next_state
        return out
