import math
from ..core.types import ShiftResult
class ShiftDetector:
    def __init__(self, reference, threshold=3.0):
        self.reference=[float(x) for x in reference]; self.threshold=float(threshold)
        if not self.reference: raise ValueError('reference cannot be empty')
    def score(self, state):
        x=state.features if hasattr(state,'features') else state
        x=[float(v) for v in x]; n=min(len(x),len(self.reference))
        if n==0:return 0.0
        return math.sqrt(sum((x[i]-self.reference[i])**2 for i in range(n))/n)
    def evaluate(self,state):
        s=self.score(state); ratio=s/self.threshold if self.threshold else float('inf')
        sev='NORMAL' if ratio<0.5 else 'WARNING' if ratio<1 else 'SHIFT' if ratio<2 else 'SEVERE'
        return ShiftResult(s,sev,s>=self.threshold)
