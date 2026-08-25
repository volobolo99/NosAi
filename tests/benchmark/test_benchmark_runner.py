from app.benchmark.runner import BenchmarkConfig, BenchmarkRunner


def test_ablation_report_is_complete():
    cfg = BenchmarkConfig(name="smoke", episodes=3, max_steps=5, simulations=8, horizon=2, seed=7)
    report = BenchmarkRunner(cfg).run_ablation()
    assert report.baseline.config == "baseline"
    assert [r.config for r in report.ablations] == ["m1", "m2", "m3", "m4"]
    assert all(r.metrics.episodes == 3 for r in report.ablations)
    assert set(report.deltas) == {"m1", "m2", "m3", "m4"}


def test_benchmark_is_reproducible_ignoring_wall_clock():
    cfg = BenchmarkConfig(name="repro", episodes=5, max_steps=5, simulations=8, horizon=2, seed=17)
    a = BenchmarkRunner(cfg).run_ablation()
    b = BenchmarkRunner(cfg).run_ablation()
    assert a.baseline.metrics.mean_reward == b.baseline.metrics.mean_reward
    assert a.baseline.metrics.success_rate == b.baseline.metrics.success_rate
    assert [(x.config, x.metrics.mean_reward, x.metrics.mean_steps) for x in a.ablations] == [
        (x.config, x.metrics.mean_reward, x.metrics.mean_steps) for x in b.ablations
    ]


def test_m4_reports_adaptive_regimes():
    cfg = BenchmarkConfig(name="m4", episodes=2, max_steps=5, simulations=8, horizon=2, seed=9)
    result = BenchmarkRunner(cfg).run_level("m4")
    assert result.metrics.decisions > 0
    assert sum(result.metrics.m4_regime_counts.values()) == result.metrics.decisions
