from __future__ import annotations
import math

class ConformalUncertainty:
    """Split-conformal threshold for scalar prediction residuals."""
    def __init__(self, alpha: float=.1):
        if not 0 < alpha < 1: raise ValueError("alpha must be in (0,1)")
        self.alpha=alpha; self.threshold=None
    def fit(self, nonconformity_scores):
        scores=sorted(max(0.0,float(s)) for s in nonconformity_scores)
        if not scores: raise ValueError("scores cannot be empty")
        q=math.ceil((len(scores)+1)*(1-self.alpha))/len(scores)
        idx=min(len(scores)-1,max(0,math.ceil(q*len(scores))-1))
        self.threshold=scores[idx]
        return self.threshold
    def interval(self, prediction: float):
        if self.threshold is None: raise RuntimeError("conformal model is not fitted")
        return (prediction-self.threshold,prediction+self.threshold)
    def is_unusual(self, score: float) -> bool:
        if self.threshold is None: raise RuntimeError("conformal model is not fitted")
        return float(score)>self.threshold
