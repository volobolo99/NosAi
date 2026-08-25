from app.benchmark.runner import BenchmarkConfig
from app.benchmark.runtime_profile import profile_benchmark


def test_runtime_profile_uses_benchmark_path_and_reports_hardware():
    profile, report = profile_benchmark(
        BenchmarkConfig(episodes=1, max_steps=2, simulations=2, horizon=1),
        levels=("baseline", "m4"),
        top_functions=3,
    )

    assert profile.levels == ("baseline", "m4")
    assert profile.wall_time_s >= 0.0
    assert profile.peak_python_memory_mb >= 0.0
    assert profile.hardware["cpu_threads"] >= 1
    assert set(result.config for result in (report.baseline, *report.ablations)) == {"baseline", "m4"}
