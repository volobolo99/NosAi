"""Hardware-aware AutoSet controller for NosAi.

AutoSet detects the host, runs the deterministic benchmark when requested, and
returns a conservative runtime profile. It only prepares process-local settings;
it never changes Windows power plans, registry values, GPU drivers, or the game.
"""
from __future__ import annotations

import os
import platform
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from app.hardware_profile import HardwareProfile, detect_hardware


@dataclass(frozen=True)
class AutoSetProfile:
    platform: str
    cpu_threads: int
    worker_threads: int
    ram_total_gb: float
    ram_budget_gb: float
    online_device: str
    training_device: str
    torch_threads: int
    benchmark_enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _ram_total_gb() -> float:
    try:
        import psutil
        return round(psutil.virtual_memory().total / (1024**3), 2)
    except ImportError:
        return 0.0


def build_profile(hardware: HardwareProfile | None = None) -> AutoSetProfile:
    hw = hardware or detect_hardware()
    torch_threads = max(1, min(4, hw.worker_threads))
    return AutoSetProfile(
        platform=platform.platform(),
        cpu_threads=hw.cpu_threads,
        worker_threads=hw.worker_threads,
        ram_total_gb=_ram_total_gb(),
        ram_budget_gb=hw.ram_budget_gb,
        online_device=hw.online_device,
        training_device=hw.training_device,
        torch_threads=torch_threads,
    )


def apply_process_settings(profile: AutoSetProfile) -> dict[str, Any]:
    """Apply safe process-local CPU settings and return what was applied."""
    os.environ["OMP_NUM_THREADS"] = str(profile.torch_threads)
    os.environ["MKL_NUM_THREADS"] = str(profile.torch_threads)
    applied: dict[str, Any] = {
        "OMP_NUM_THREADS": profile.torch_threads,
        "MKL_NUM_THREADS": profile.torch_threads,
    }
    try:
        import torch
        torch.set_num_threads(profile.torch_threads)
        applied["torch_threads"] = torch.get_num_threads()
    except Exception:
        applied["torch_threads"] = None
    return applied


def run_benchmark(output: str | Path | None = None) -> dict[str, Any]:
    """Run the existing deterministic baseline/M1-M4 benchmark and return a dict."""
    from app.benchmark.runner import BenchmarkConfig, BenchmarkRunner

    started = time.perf_counter()
    runner = BenchmarkRunner(BenchmarkConfig(name="autoset", episodes=25, seed=42))
    report = runner.run_ablation()
    payload = report.to_dict()
    payload["elapsed_s"] = round(time.perf_counter() - started, 4)
    if output is not None:
        report.save(output)
    return payload


def autoset(*, benchmark: bool = True, output: str | Path | None = None) -> dict[str, Any]:
    """Detect -> benchmark -> apply, with an auditable result."""
    profile = build_profile()
    applied = apply_process_settings(profile)
    result: dict[str, Any] = {"profile": profile.to_dict(), "applied": applied}
    result["benchmark"] = run_benchmark(output) if benchmark else None
    result["status"] = "READY"
    result["safety"] = {
        "process_local_only": True,
        "game_control": False,
        "registry_changes": False,
        "power_plan_changes": False,
    }
    return result


__all__ = ["AutoSetProfile", "apply_process_settings", "autoset", "build_profile", "run_benchmark"]
