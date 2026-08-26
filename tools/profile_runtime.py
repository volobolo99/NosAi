"""Run the deterministic NosAi runtime profiler and write a JSON report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.benchmark.runtime_profile import profile_benchmark
from app.benchmark.runner import BenchmarkConfig


def main() -> int:
    parser = argparse.ArgumentParser(description="Profile the deterministic NosAi benchmark")
    parser.add_argument("--output", type=Path, default=Path("runtime_profile.json"))
    parser.add_argument("--episodes", type=int, default=20)
    parser.add_argument("--max-steps", type=int, default=10)
    parser.add_argument("--simulations", type=int, default=32)
    parser.add_argument("--horizon", type=int, default=3)
    args = parser.parse_args()

    config = BenchmarkConfig(
        name="runtime-profile",
        episodes=args.episodes,
        max_steps=args.max_steps,
        simulations=args.simulations,
        horizon=args.horizon,
    )
    profile, report = profile_benchmark(config=config)
    payload = {
        "schema": 1,
        "profile": profile.to_dict(),
        "benchmark": report.to_dict(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"runtime profile written to {args.output}")
    print(f"wall_time_s={profile.wall_time_s:.6f}")
    print(f"peak_python_memory_mb={profile.peak_python_memory_mb:.3f}")
    if profile.cuda_peak_allocated_mb is not None:
        print(f"cuda_peak_allocated_mb={profile.cuda_peak_allocated_mb:.3f}")
        print(f"cuda_peak_reserved_mb={profile.cuda_peak_reserved_mb:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
