from app.benchmark.multiobjective import EpisodeOutcome, ObjectiveWeights, score_episode, summarize, aggregate
from app.benchmark.stress_runner import StressBenchmarkRunner, StressConfig

def test_multiobjective_penalizes_risk_and_failure():
    w = ObjectiveWeights()
    safe = score_episode(EpisodeOutcome(10, 2, True, 0.0, 0.0, 0.0), w, 10)
    risky = score_episode(EpisodeOutcome(10, 2, True, 1.0, 0.0, 0.0), w, 10)
    failed = score_episode(EpisodeOutcome(10, 2, False, 0.0, 0.0, 0.0), w, 10)
    assert safe > risky > failed

def test_stress_runner_is_reproducible():
    cfg = StressConfig(episodes_per_scenario=2, max_steps=8, simulations=4, horizon=2, seed=9)
    a = StressBenchmarkRunner(cfg).run()
    b = StressBenchmarkRunner(cfg).run()
    assert [x.to_dict() for x in a] == [x.to_dict() for x in b]

def test_stress_report_contains_all_scenarios():
    cfg = StressConfig(episodes_per_scenario=1, max_steps=6, simulations=2, horizon=2, seed=3)
    results = StressBenchmarkRunner(cfg).run()
    assert {r.level for r in results} == {'baseline','m1','m2','m3','m4'}
    assert all(len(r.report.scenarios) >= 6 for r in results)
