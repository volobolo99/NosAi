from app.m13.evaluation import ScientificEvaluator, EvaluationResult

def test_ablation_delta(): assert ScientificEvaluator().ablation(1,2)['delta']==1

def test_multi_seed(): assert ScientificEvaluator().multi_seed([1,2,3])['mean']==2

def test_leaderboard():
    r=ScientificEvaluator().leaderboard([EvaluationResult('a',1,1),EvaluationResult('b',1,2)]); assert r[0].name=='b'
