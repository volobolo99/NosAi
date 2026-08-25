"""End-to-end local Test Pilot cycle.

The cycle runs safe scenarios, writes JSON/HTML reports, updates the learning
ledger, and creates a repair queue. It never edits source code by itself.
Source changes remain a separate gated step so corrupted telemetry cannot
silently rewrite the application.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .adapters import SimulatedClientAdapter
from .learning import update_learning_ledger, write_repair_queue
from .models import PilotMode, PilotSessionConfig
from .reporting import write_html_report, write_json_report
from .runner import TestPilot
from .system import collect_system_profile, write_system_profile


DEFAULT_SCENARIOS = ("combat_basic", "missing_target", "stale_state")


def run_cycle(
    *,
    scenarios: Iterable[str] = DEFAULT_SCENARIOS,
    ticks: int = 500,
    mode: PilotMode = PilotMode.SIMULATION,
    output_dir: str | Path = "artifacts/pilot",
) -> dict[str, object]:
    """Run all safe local scenarios and persist diagnostics and learning data."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    profile_path = write_system_profile(collect_system_profile(), root / "system_profile.json")
    all_errors: list[dict] = []
    reports: list[dict[str, str]] = []

    for scenario in scenarios:
        telemetry = root / f"{scenario}.jsonl"
        result = TestPilot(
            SimulatedClientAdapter(scenario=scenario),
            PilotSessionConfig(mode=mode, ticks=ticks, telemetry_path=str(telemetry)),
        ).run()
        json_path = write_json_report(result, root / f"{scenario}.report.json")
        html_path = write_html_report(result, root / f"{scenario}.report.html")
        all_errors.extend(asdict(error) for error in result.errors)
        reports.append({"scenario": scenario, "json": str(json_path), "html": str(html_path), "telemetry": str(telemetry)})

    ledger = update_learning_ledger(all_errors, "multi-scenario", root / "learning_ledger.json")
    queue = write_repair_queue(ledger, root / "repair_queue.json")
    return {
        "system_profile": str(profile_path),
        "reports": reports,
        "learning_ledger": str(root / "learning_ledger.json"),
        "repair_queue": str(queue),
        "error_count": len(all_errors),
        "ready_for_live_action": False,
    }
