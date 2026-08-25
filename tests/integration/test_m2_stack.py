from app.m1.core.types import State, Action
from app.m2 import M2Planner

class WM:
    def predict(self,s,a):
        from app.m1.core.types import Prediction, Uncertainty
        d=float(a.parameters['d']); return Prediction(State((s.features[0]+d,),s.timestamp+1),d,0.0,d)
    def uncertainty(self,s,a):
        from app.m1.core.types import Uncertainty
        return Uncertainty(epistemic=.05,aleatoric=.01,confidence=.94)

def test_full_m2_flow():
    p=M2Planner(WM(),seed=7,max_uncertainty=1)
    actions=[Action('a',{'d':1}),Action('b',{'d':2})]
    result=p.plan(State((0.,)),actions,simulations=12,horizon=3)
    assert len(result.actions)==3
    assert result.uncertainty >= 0
