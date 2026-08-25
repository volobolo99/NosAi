import math
from ..core.types import OODResult
class OODDetector:
    def __init__(self, reference, threshold=3.0):
        self.reference=[float(x) for x in reference]; self.threshold=float(threshold)
    def score(self,state):
        x=state.features if hasattr(state,'features') else state; x=[float(v) for v in x]; n=min(len(x),len(self.reference))
        if n==0:return 0.0
        return math.sqrt(sum((x[i]-self.reference[i])**2 for i in range(n))/n)
    def evaluate(self,state):
        s=self.score(state); p=1-math.exp(-s/max(self.threshold,1e-8)); return OODResult(s,p,max(0.0,1-p),s>=self.threshold)
