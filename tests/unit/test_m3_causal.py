from app.m3.graph import CausalGraph
from app.m3.simulator import CausalSimulator
from app.m3.counterfactual_memory import CounterfactualMemory
from app.m3.meta_learner import MetaLearner

def test_causal_intervention_propagates():
    g=CausalGraph(); g.add_edge("action","reward",2.0)
    sim=CausalSimulator(g,{"reward":lambda v: 1.0+v["action"]*2.0})
    assert sim.simulate({"action":0}) .values["reward"] == 1.0
    assert sim.effect({"action":0},{"action":2},"reward") == 4.0

def test_cycle_is_rejected():
    g=CausalGraph(); g.add_edge("a","b")
    try: g.add_edge("b","a")
    except ValueError: return
    assert False

def test_counterfactual_memory():
    m=CounterfactualMemory(); m.add({"x":1},{"a":2},1,4,.5)
    assert m.mean_effect({"a":2}) == 3.0

def test_meta_learner_updates():
    m=MetaLearner({"x":0.0},learning_rate=.1)
    before=m.score({"x":1})
    m.update({"x":1},1.0)
    assert m.score({"x":1}) > before
