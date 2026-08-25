"""Command-line entry point for the safe local Test Pilot."""

from __future__ import annotations

import argparse
import json

from .adapters import SimulatedClientAdapter
from .models import PilotMode, PilotSessionConfig
from .runner import TestPilot


def main() -> int:
    parser = argparse.ArgumentParser(description="Run NosAi Test Pilot in a safe non-live mode")
    parser.add_argument("--scenario", default="combat_basic", choices=("combat_basic", "missing_target", "stale_state"))
    parser.add_argument("--ticks", type=int, default=100)
    parser.add_argument("--mode", choices=("simulation", "shadow", "dry_run"), default="simulation")
    parser.add_argument("--telemetry", default="artifacts/pilot/telemetry.jsonl")
    args = parser.parse_args()

    if args.ticks < 1:
        parser.error("--ticks must be >= 1")

    result = TestPilot(
        SimulatedClientAdapter(scenario=args.scenario),
        PilotSessionConfig(
            mode=PilotMode(args.mode),
            ticks=args.ticks,
            telemetry_path=args.telemetry,
        ),
    ).run()

    print(json.dumps({
        "session_id": result.session_id,
        "mode": result.mode.value,
        "ticks": result.ticks,
        "decisions": result.decisions,
        "valid_decisions": result.valid_decisions,
        "missing_capabilities": result.missing_capabilities,
        "avg_decision_latency_ms": result.avg_decision_latency_ms,
        "error_count": len(result.errors),
        "ready_for_live_action": result.ready_for_live_action,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
