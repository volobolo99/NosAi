from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Callable, Any

@dataclass(frozen=True)
class RobustnessReport:
    adversarial_score: float; rare_event_score: float; observation_quality: float; failure_probability: float; safe_fallback: bool
    stress_cases: int=0

class RobustnessEngine:
    def adversarial_score(self,nominal,perturbed):
        rows=list(perturbed)
        if not rows:return 1.0
        return max(0.0,min(1.0,1.0-sum(abs(x-nominal) for x in rows)/len(rows)))
    def rare_event_score(self,failures,trials): return 1.0 if trials<=0 else max(0.0,min(1.0,1.0-failures/trials))
    def observation_quality(self,observed,expected):
        a=list(observed);b=list(expected)
        if not a or len(a)!=len(b):return 0.0
        err=sum(abs(x-y) for x,y in zip(a,b))/len(a);return 1/(1+err)
    def predict_failure(self,risk,uncertainty,threshold=.7): return .7*risk+.3*uncertainty>=threshold
    def safe_action(self,preferred,fallback,*,failure_probability,threshold=.7): return fallback if failure_probability>=threshold else preferred
    def perturbations(self,value,epsilon=.1,count=5): return [value-epsilon,value+epsilon]+[value+(epsilon*(i-(count-1)/2)/(count or 1)) for i in range(count)]
    def stress(self,fn:Callable[[Any],Any],cases:Iterable[Any],fallback:Any=None):
        outputs=[]; failures=0
        for case in cases:
            try: outputs.append(fn(case))
            except Exception: failures+=1; outputs.append(fallback)
        return outputs,failures
    def report(self,nominal,perturbed,failures,trials,observed,expected,risk,uncertainty):
        fp=.7*risk+.3*uncertainty
        return RobustnessReport(self.adversarial_score(nominal,perturbed),self.rare_event_score(failures,trials),self.observation_quality(observed,expected),fp,fp>=.7,len(list(perturbed)))
