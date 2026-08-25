from app.m11.unified_planner import UnifiedPlanner

def test_strategy_selection_and_budget():
    p=UnifiedPlanner(); d=p.fuse([{'action':'a','score':2,'risk':0,'uncertainty':0,'confidence':1},{'action':'b','score':1,'risk':0,'uncertainty':0,'confidence':1}],uncertainty=.1,risk=.1)
    assert d.action=='a' and d.compute_budget>32

def test_safe_strategy_on_high_risk():
    d=UnifiedPlanner().fuse([{'action':'a','score':2,'risk':1,'uncertainty':0,'confidence':1}],uncertainty=.1,risk=.8)
    assert d.rationale==('safe',)
