"""Deterministic CPU/memory profiling for the NosAi benchmark harness.

This module profiles the same benchmark path used for regression/ablation rather than
inventing a synthetic workload. It deliberately has no third-party profiling dependency:
CPU timing comes from ``cProfile`` and Python allocations from ``tracemalloc``.
CUDA memory is reported when PyTorch/CUDA is available, but GPU profiling is never required.
"""
from __future__ import annotations

import cProfile
import io
import pstats
import tracemalloc
from dataclasses import asdict, dataclass
from typing import Iterable

from app.benchmark.runner import BenchmarkConfig, BenchmarkReport, BenchmarkRunner
from app.hardware_profile import detect_hardware


@dataclass(frozen=True)
class RuntimeProfile:
    levels: tuple[str, ...]
    wall_time_s: float
    peak_python_memory_mb: float
    cpu_top_functions: tuple[str, ...]
    cuda_peak_allocated_mb: float | None
    cuda_peak_reserved_mb: float | None
    hardware: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def profile_benchmark(
    config: BenchmarkConfig | None = None,
    levels: Iterable[str] = ("baseline", "m1", "m2", "m3", "m4"),
    top_functions: int = 12,
) -> tuple[RuntimeProfile, BenchmarkReport]:
    """Profile the deterministic benchmark and return both profile and benchmark report."""
    config = config or BenchmarkConfig(episodes=25, max_steps=10, simulations=32, horizon=3)
    selected_levels = tuple(levels)
    runner = BenchmarkRunner(config)
    profiler = cProfile.Profile()

    cuda_peak_allocated_mb: float | None = None
    cuda_peak_reserved_mb: float | None = None
    try:
        import torch
    except ImportError:
        torch = None

    cuda_enabled = bool(torch is not None and torch.cuda.is_available())
    if cuda_enabled:
        torch.cuda.reset_peak_memory_stats()

    tracemalloc.start()
    profiler.enable()
    report = runner.run_ablation(selected_levels)
    profiler.disable()
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if cuda_enabled:
        cuda_peak_allocated_mb = torch.cuda.max_memory_allocated() / (1024**2)
        cuda_peak_reserved_mb = torch.cuda.max_memory_reserved() / (1024**2)

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumtime")
    stats.print_stats(top_functions)
    lines = tuple(line.rstrip() for line in stream.getvalue().splitlines() if line.strip())
    hardware = asdict(detect_hardware())
    hardware["cuda_available"] = cuda_enabled

    wall_time_s = sum(result.metrics.wall_time_s for result in (report.baseline, *report.ablations))
    return (
        RuntimeProfile(
            levels=selected_levels,
            wall_time_s=wall_time_s,
            peak_python_memory_mb=peak_bytes / (1024**2),
            cpu_top_functions=lines,
            cuda_peak_allocated_mb=cuda_peak_allocated_mb,
            cuda_peak_reserved_mb=cuda_peak_reserved_mb,
            hardware=hardware,
        ),
        report,
    )
