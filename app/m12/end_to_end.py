from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable

@dataclass(frozen=True)
class Outcome:
    action: str; reward: float; success: bool

class EndToEndLearningLoop:
    def __init__(self,learning_rate=.05):self.learning_rate=learning_rate;self.weights={};self.history=[];self.steps=0
    def observe(self,outcome):
        self.history.append(outcome);self.steps+=1;old=self.weights.get(outcome.action,0.0);target=outcome.reward+(1 if outcome.success else 0);self.weights[outcome.action]=old+self.learning_rate*(target-old);return self.weights[outcome.action]
    def preferred(self):return max(self.weights,key=self.weights.get) if self.weights else None
    def run(self,actions,environment:Callable[[str],Outcome],episodes=1):
        for _ in range(episodes):
            for action in actions:self.observe(environment(action))
        return self.preferred()

class PlannerLearner:
    def __init__(self,learning_rate=1.0):self.learning_rate=learning_rate
    def update(self,scores,outcome):
        out=dict(scores);out[outcome.action]=out.get(outcome.action,0)+self.learning_rate*outcome.reward;return out

class WorldModelCoTrainer:
    def __init__(self,model):self.model=model;self.errors=[]
    def train_step(self,prediction_error):
        self.errors.append(float(prediction_error))
        if hasattr(self.model,'update'):return float(self.model.update(prediction_error))
        return float(prediction_error)
    def mean_error(self):return sum(self.errors)/len(self.errors) if self.errors else 0.0

class MetaLearner:
    def __init__(self,step=.05):self.step=step;self.learning_rate=step;self.history=[]
    def adapt(self,improvement):
        self.learning_rate=max(.001,min(1.0,self.learning_rate+self.step*(1 if improvement>0 else -1)));self.history.append((improvement,self.learning_rate));return self.learning_rate
    def fit(self,improvements):
        for x in improvements:self.adapt(x)
        return self.learning_rate

class WeightOptimizer:
    def optimize(self,weights,losses):
        keys=set(weights)|set(losses);raw={k:max(0.0,float(weights.get(k,0))-0.1*float(losses.get(k,0))) for k in keys};total=sum(raw.values());return {k:v/total for k,v in raw.items()} if total else {k:1/len(raw) for k in raw} if raw else {}
    def gradient_step(self,weights,gradients,lr=.1):return self.optimize(weights,{k:-lr*g for k,g in gradients.items()})
