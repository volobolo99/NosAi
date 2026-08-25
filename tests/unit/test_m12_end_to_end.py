from app.m12.end_to_end import EndToEndLearningLoop, Outcome, PlannerLearner, MetaLearner, WeightOptimizer

def test_action_outcome_loop_learns_preference():
    l=EndToEndLearningLoop(); l.observe(Outcome('a',1,True)); l.observe(Outcome('b',0,False)); assert l.preferred()=='a'

def test_planner_learning_updates_score():
    assert PlannerLearner().update({'a':0},Outcome('a',2,True))['a']==2

def test_meta_learning_adapts():
    m=MetaLearner(); assert m.adapt(1)>.05

def test_weight_optimizer_normalizes():
    out=WeightOptimizer().optimize({'a':.5,'b':.5},{'a':0,'b':1}); assert abs(sum(out.values())-1)<1e-9
