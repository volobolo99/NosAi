from __future__ import annotations
from dataclasses import dataclass
from copy import deepcopy
from typing import Callable

@dataclass(frozen=True)
class LearningEvent:
    key: str; value: float; importance: float=1.0
@dataclass(frozen=True)
class ModelSnapshot:
    version: int; state: dict[str,float]
@dataclass(frozen=True)
class CurriculumState:
    difficulty: float; success_rate: float

class ContinualLearningEngine:
    def __init__(self, learning_rate=.1, importance_floor=.25, forgetting=.01):
        self.learning_rate=float(learning_rate); self.importance_floor=float(importance_floor); self.forgetting=float(forgetting)
        self.state={}; self.importance={}; self.version=0; self.snapshots=[]; self.history=[]
    def update(self,event):
        old=self.state.get(event.key,0.0); protected=self.importance.get(event.key,0.0)
        rate=self.learning_rate if event.importance>=protected else self.learning_rate*.25
        self.state[event.key]=old+rate*(event.value-old)
        self.importance[event.key]=max(protected,event.importance,self.importance_floor if event.importance>0 else 0)
        self.version+=1; self.history.append(event); return self.state[event.key]
    def consolidate(self):
        self.snapshots.append(ModelSnapshot(self.version,deepcopy(self.state))); return self.snapshots[-1]
    def rollback(self,version=None):
        if not self.snapshots:return False
        choices=[s for s in self.snapshots if version is None or s.version<=version]
        if not choices:return False
        snap=max(choices,key=lambda s:s.version); self.state=deepcopy(snap.state); self.version=snap.version; return True
    def protect(self,key,importance=1.0): self.importance[key]=max(self.importance.get(key,0.0),float(importance))
    def prevent_forgetting(self):
        for k,v in list(self.state.items()):
            imp=self.importance.get(k,0.0)
            self.state[k]=v if imp>=self.importance_floor else v*(1.0-self.forgetting)
        return dict(self.state)
    def replay(self,events,filter_fn=None):
        for e in events:
            if filter_fn is None or filter_fn(e): self.update(e)
        return dict(self.state)

class CurriculumScheduler:
    def __init__(self,initial=.1,step=.05,maximum=1.0,minimum=0.0): self.difficulty=initial; self.step=step; self.maximum=maximum; self.minimum=minimum; self.history=[]
    def update(self,success_rate):
        if success_rate>=.8:self.difficulty=min(self.maximum,self.difficulty+self.step)
        elif success_rate<.4:self.difficulty=max(self.minimum,self.difficulty-self.step)
        self.history.append(CurriculumState(self.difficulty,float(success_rate))); return self.difficulty
    def curriculum(self,success_rates): return [self.update(x) for x in success_rates]
