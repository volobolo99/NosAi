from __future__ import annotations
from dataclasses import dataclass
from statistics import mean,stdev
import json
from pathlib import Path

@dataclass(frozen=True)
class EvaluationResult:
    name:str; seed:int; score:float

class ScientificEvaluator:
    def ablation(self,baseline,variant):return {'baseline':baseline,'variant':variant,'delta':variant-baseline,'improvement_ratio':(variant-baseline)/abs(baseline) if baseline else float('inf')}
    def cross_scenario(self,scores):
        vals=list(scores.values());return {'scores':dict(scores),'mean':mean(vals) if vals else 0.0,'min':min(vals) if vals else 0.0,'max':max(vals) if vals else 0.0}
    def multi_seed(self,scores):
        return {'mean':mean(scores),'std':stdev(scores) if len(scores)>1 else 0.0,'n':len(scores),'min':min(scores) if scores else 0.0,'max':max(scores) if scores else 0.0}
    def confidence_interval(self,scores):
        s=self.multi_seed(scores); margin=1.96*s['std']/(s['n']**.5) if s['n']>1 else 0.0;return {'mean':s['mean'],'low':s['mean']-margin,'high':s['mean']+margin}
    def save_regression(self,path,results):Path(path).write_text(json.dumps([r.__dict__ for r in results],indent=2));return path
    def load_regression(self,path):return [EvaluationResult(**x) for x in json.loads(Path(path).read_text())]
    def compare_regression(self,current,baseline,tolerance=0.0):return current>=baseline-tolerance
    def leaderboard(self,results):return sorted(results,key=lambda r:r.score,reverse=True)
