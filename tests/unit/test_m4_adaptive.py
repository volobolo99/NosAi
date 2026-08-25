from app.m4.adaptive import AdaptivePlanner, PlannerRegime


def test_adaptive_budget_rises_with_uncertainty():
    p = AdaptivePlanner(min_simulations=10, max_simulations=100, min_horizon=2, max_horizon=10)
    low = p.decide(uncertainty=0.0, ood=0.0, shift=0.0, action_count=1)
    high = p.decide(uncertainty=1.0, ood=1.0, shift=1.0, action_count=8)
    assert high.simulations >= low.simulations
    assert high.horizon >= low.horizon
    assert high.risk_penalty >= low.risk_penalty


def test_adaptive_update_is_bounded():
    p = AdaptivePlanner()
    d = p.decide(uncertainty=.8, ood=.2, shift=.1)
    for _ in range(1000):
        p.update(d, 1.0)
    assert all(-1.0 <= v <= 1.0 for v in p.snapshot().values())


def test_same_inputs_are_deterministic():
    p = AdaptivePlanner(seed=7)
    assert p.decide(uncertainty=.2, ood=.1, shift=.3, action_count=4) == p.decide(uncertainty=.2, ood=.1, shift=.3, action_count=4)
