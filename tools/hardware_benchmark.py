"""Run a reproducible hardware-aware NosAi benchmark.

The benchmark is intentionally conservative: it measures the deterministic
runtime workload without requiring CUDA, while collecting CPU/RAM/VRAM data
when available. Results are written as JSON for before/after comparisons.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import time
import tracemalloc
from pathlib import Path

from app.benchmark.runtime_profile import profile_benchmark


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/hardware_benchmark.json"))
    args = parser.parse_args()

    tracemalloc.start()
    started = time.perf_counter()
    result = profile_benchmark()
    elapsed = time.perf_counter() - started
    _, peak_python = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    payload = {
        "schema": 1,
        "hardware": {
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
            "python": platform.python_version(),
        },
        "benchmark": result,
        "measurement": {
            "wall_time_s": elapsed,
            "peak_python_bytes": peak_python,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
