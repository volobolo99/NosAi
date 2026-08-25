from app.m1.core.types import Action, State, Prediction, Uncertainty
from app.m2 import ImaginationEngine, M2Planner, UncertaintyCalibrator, ConformalUncertainty
from app.m2.causal import CounterfactualEngine

class ToyWM:
    def predict(self,s,a):
        d=float(a.parameters.get('delta',0)); r=float(a.parameters.get('reward',d))
        ns=State((float(s.features[0])+d,),s.timestamp+1,s.scenario_id,s.metadata)
        return Prediction(ns,r,0.0,r)
    def uncertainty(self,s,a):
        return Uncertainty(epistemic=0.1 if a.id=='safe' else 0.4,aleatoric=0.0,confidence=.9)

def actions(): return [Action('safe',{'delta':1,'reward':2}),Action('risky',{'delta':-1,'reward':3})]

def test_imagination_multistep():
    t=ImaginationEngine(ToyWM()).rollout(State((0.,)),actions())
    assert len(t.steps)==2 and t.total_reward==5

def test_m2_planner_returns_plan():
    r=M2Planner(ToyWM(),seed=1).plan(State((0.,)),actions(),simulations=16,horizon=2)
    assert r.actions and r.simulations==16

def test_counterfactual():
    e=CounterfactualEngine(ImaginationEngine(ToyWM()))
    r=e.compare(State((0.,)),[actions()[0]],[actions()[1]])
    assert r.delta_return != 0 and 0 < r.confidence <= 1

def test_calibration_and_conformal():
    c=UncertaintyCalibrator(); c.fit([.1,.2,.3,.4]); assert 0<=c.transform(.25).calibrated_uncertainty<=1
    q=ConformalUncertainty(.1); threshold=q.fit([1,2,3,4]); assert threshold>=3 and q.interval(10)[0] < 10
