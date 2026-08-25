from app.m1.core.types import State, Action, Prediction, Uncertainty
from app.m1.integration import M1LearningStack
from app.m2.integration import M2PlanningStack
from app.m3 import M3PlanningStack, CausalGraph
from app.world_model.state import WorldState
from app.world_model.actions import WorldAction

class WM:
    def predict(self,s,a):
        d=float(a.parameters.get('d',0)); return Prediction(State((s.features[0]+d,),s.timestamp+1),d,0.0,d)
    def uncertainty(self,s,a): return Uncertainty(.05,.01,confidence=.94)

def test_m3_over_m2():
    class Dummy: pass
    m1=Dummy(); m1.world_model=WM()
    m2=M2PlanningStack(m1,simulations=8,horizon=2)
    g=CausalGraph(); g.add_edge('action','value')
    m3=M3PlanningStack(m2,g,{'value':lambda v: v.get('action',0)*2})
    ws=WorldState(character={'hp':100,'mp':50})
    action,result=m3.choose(ws,[WorldAction('a','move',{'d':1}),WorldAction('b','move',{'d':2})])
    assert action is not None
    assert len(result.actions)==2
