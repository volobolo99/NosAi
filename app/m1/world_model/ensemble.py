"""Uncertainty-aware World Model ensemble."""
from __future__ import annotations
import statistics
from ..core.types import Prediction, Uncertainty
from .base import WorldModel


class WorldModelEnsemble(WorldModel):
    def __init__(self, models):
        if len(models) < 2:
            raise ValueError('at least two independent models required')
        self.models = list(models)

    def model_predictions(self, state, action):
        return [m.predict(state, action) for m in self.models]

    @staticmethod
    def _aggregate(ps):
        rewards = [p.reward for p in ps]
        vals = [p.value for p in ps]
        dones = [p.done_probability for p in ps]
        return Prediction(ps[0].next_state, statistics.fmean(rewards), statistics.fmean(dones), statistics.fmean(vals))

    @staticmethod
    def _uncertainty_from_predictions(ps):
        if len(ps) < 2:
            return Uncertainty(epistemic=0.0, aleatoric=0.0, confidence=1.0)
        reward_d = statistics.pvariance([p.reward for p in ps])
        vecs = []
        for p in ps:
            x = getattr(p.next_state, 'features', None)
            if x is not None:
                vecs.append(tuple(float(v) for v in x))
        state_d = 0.0
        if len(vecs) >= 2:
            dims = min(map(len, vecs))
            state_d = sum(statistics.pvariance([v[d] for v in vecs]) for d in range(dims)) / dims
        epistemic = float(reward_d + state_d)
        return Uncertainty(epistemic=epistemic, aleatoric=0.0, confidence=1 / (1 + epistemic))

    def evaluate(self, state, action):
        """Return prediction and epistemic uncertainty from one ensemble pass."""
        predictions = self.model_predictions(state, action)
        return self._aggregate(predictions), self._uncertainty_from_predictions(predictions)

    def predict(self, state, action):
        return self.evaluate(state, action)[0]

    def disagreement(self, state, action):
        predictions = self.model_predictions(state, action)
        if len(predictions) < 2:
            return 0.0
        return float(statistics.pvariance([p.reward for p in predictions]))

    def state_disagreement(self, state, action):
        predictions = self.model_predictions(state, action)
        vecs = []
        for p in predictions:
            x = getattr(p.next_state, 'features', None)
            if x is not None:
                vecs.append(tuple(float(v) for v in x))
        if len(vecs) < 2:
            return 0.0
        dims = min(map(len, vecs))
        return float(sum(statistics.pvariance([v[d] for v in vecs]) for d in range(dims)) / dims)

    def uncertainty(self, state, action):
        return self.evaluate(state, action)[1]

    def rollout(self, state, actions):
        out = []; s = state
        for a in actions:
            p = self.predict(s, a); out.append(p); s = p.next_state
        return out
