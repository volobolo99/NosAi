from app.m8.horizon import LongHorizonStrategy,HorizonStep
from app.m9.continual import ContinualLearningEngine,LearningEvent,CurriculumScheduler
from app.m10.robustness import RobustnessEngine
from app.m11.unified_planner import UnifiedPlanner
from app.m12.end_to_end import EndToEndLearningLoop,Outcome,MetaLearner,WeightOptimizer
from app.m13.evaluation import ScientificEvaluator,EvaluationResult
from app.m14.performance import ParallelSimulation,ComputeProfiler,MCTSOptimizer,MemoryIndex
from app.m15.release_gate import ReliabilityGate
from app.release_pipeline import NosAiIntegration

def test_25_long_horizon():
    p=LongHorizonStrategy(); a=p.evaluate([HorizonStep('a',2,.1,.1,0),HorizonStep('b',1,.1,.1,1)]); b=p.evaluate([HorizonStep('c',1,.1,.1,0)]); assert a.total_value>b.total_value; assert p.choose([[HorizonStep('a',2)] ,[HorizonStep('b',1)] ]).steps[0].action=='a'

def test_26_30_continual():
    e=ContinualLearningEngine();e.update(LearningEvent('x',10,1));e.consolidate();e.update(LearningEvent('x',20,1));assert e.rollback();e.protect('x',1);v=e.state['x'];e.prevent_forgetting();assert e.state['x']==v
    c=CurriculumScheduler(.5,.1,1);assert c.curriculum([.9,.9])[-1]==.7

def test_31_35_robustness():
    r=RobustnessEngine();outs,fails=r.stress(lambda x:1/x,[1,0,2],fallback=0);assert fails==1 and outs[1]==0; assert r.predict_failure(.9,.9); assert r.safe_action('a','b',failure_probability=.9)=='b'

def test_36_40_unified():
    p=UnifiedPlanner();d=p.fuse_layers(planner_candidates=[{'action':'a','score':3,'risk':.1,'uncertainty':.1,'confidence':.9}],memory_candidates=[{'action':'b','score':1,'risk':0,'uncertainty':0,'confidence':1}],uncertainty=.1,risk=.1);assert d.action=='a'

def test_41_45_e2e():
    l=EndToEndLearningLoop();l.run(['a'],lambda a:Outcome(a,1,True),2);assert l.preferred()=='a';m=MetaLearner();assert m.fit([1,-1])<.2;assert abs(sum(WeightOptimizer().optimize({'a':.5,'b':.5},{'a':0,'b':1}).values())-1)<1e-9

def test_46_50_evaluation():
    e=ScientificEvaluator();assert e.confidence_interval([1,2,3])['low']<2<e.confidence_interval([1,2,3])['high'];r=[EvaluationResult('a',1,1),EvaluationResult('b',2,2)]; assert e.leaderboard(r)[0].name=='b';assert e.compare_regression(1,1)

def test_51_55_performance():
    p=ParallelSimulation();assert p.run(lambda x:x*x,[1,2,3])==[1,4,9]; assert MCTSOptimizer().schedule(.5,.5)>64; i=MemoryIndex();i.rebuild([('x',1),('x',2)]);i.remove('x',1);assert i.get('x')==[2]

def test_56_60_release():
    g=ReliabilityGate();assert g.deterministic_hash({'b':2,'a':1})==g.deterministic_hash({'a':1,'b':2})
    evidence=g.hardened_suite(iterations=250)
    assert all(evidence[k]['passed'] for k in ('long_run','fault_injection','recovery','reproducibility'))
    assert evidence['end_to_end']['passed']

def test_end_to_end_25_60():
    n=NosAiIntegration();d=n.smoke();assert d.action=='a';a=n.audit();assert a.points==(tuple(range(25,61))) and all(a.checks.values())
