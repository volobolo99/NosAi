"""Benchmark harness for installed Ollama models.

Measures end-to-end CLI generation latency. It does not execute any game
command and only benchmarks explicitly supplied local model names.
"""
from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class BenchmarkResult:
    model: str
    ok: bool
    latency_ms: float | None
    output_chars: int = 0
    error: str | None = None


def benchmark_model(model: str, prompt: str = "Return only OK.", timeout: int = 60) -> BenchmarkResult:
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        latency = round((time.perf_counter() - start) * 1000, 1)
        if proc.returncode != 0:
            return BenchmarkResult(model, False, latency, error=proc.stderr.strip()[-500:])
        return BenchmarkResult(model, bool(proc.stdout.strip()), latency, len(proc.stdout.strip()))
    except (OSError, subprocess.SubprocessError) as exc:
        return BenchmarkResult(model, False, None, error=str(exc))


def benchmark_installed(candidates: tuple[str, ...] = ("qwen3:4b", "qwen3:8b", "qwen3:14b")) -> list[dict]:
    results = []
    for model in candidates:
        result = benchmark_model(model)
        results.append(asdict(result))
    return results
