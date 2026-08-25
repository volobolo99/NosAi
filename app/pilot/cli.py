"""Command-line entry point for the safe local Test Pilot."""

from __future__ import annotations

import argparse
import json

from .adapters import SimulatedClientAdapter
from .cycle import run_cycle
from .models import PilotMode, PilotSessionConfig
from .reporting import write_html_report, write_json_report
from .runner import TestPilot


SCENARIOS = ("combat_basic", "missing_target", "stale_state")


def _single_run(args: argparse.Namespace) -> dict:
    """Run one deterministic scenario and return its diagnostic summary."""
    result = TestPilot(
        SimulatedClientAdapter(scenario=args.scenario),
        PilotSessionConfig(
            mode=PilotMode(args.mode),
            ticks=args.ticks,
            telemetry_path=args.telemetry,
        ),
    ).run()
    if args.report_dir:
        write_json_report(result, f"{args.report_dir}/{args.scenario}.report.json")
        write_html_report(result, f"{args.report_dir}/{args.scenario}.report.html")
    return {
        "session_id": result.session_id,
        "mode": result.mode.value,
        "ticks": result.ticks,
        "decisions": result.decisions,
        "valid_decisions": result.valid_decisions,
        "blocked_decisions": result.blocked_decisions,
        "state_quality_counts": result.state_quality_counts,
        "missing_capabilities": result.missing_capabilities,
        "avg_decision_latency_ms": result.avg_decision_latency_ms,
        "error_count": len(result.errors),
        "ready_for_live_action": result.ready_for_live_action,
    }


def main() -> int:
    """Parse CLI options, run the requested safe diagnostic mode, and print JSON."""
    parser = argparse.ArgumentParser(description="Run NosAi Test Pilot in safe non-live modes")
    parser.add_argument("--scenario", default="combat_basic", choices=SCENARIOS)
    parser.add_argument("--all-scenarios", action="store_true", help="Run the complete safe diagnostic suite")
    parser.add_argument("--ticks", type=int, default=100)
    parser.add_argument("--mode", choices=("simulation", "shadow", "dry_run"), default="simulation")
    parser.add_argument("--telemetry", default="artifacts/pilot/telemetry.jsonl")
    parser.add_argument("--report-dir", default="artifacts/pilot")
    parser.add_argument("--cycle", action="store_true", help="Run scenarios, reports, learning ledger and repair queue")
    args = parser.parse_args()

    if args.ticks < 1:
        parser.error("--ticks must be >= 1")

    if args.cycle or args.all_scenarios:
        result = run_cycle(
            scenarios=SCENARIOS,
            ticks=args.ticks,
            mode=PilotMode(args.mode),
            output_dir=args.report_dir,
        )
    else:
        result = _single_run(args)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
