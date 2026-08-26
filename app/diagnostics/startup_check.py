"""Deterministic startup diagnostics for NosAi.

This module validates configuration and internal contracts without touching the
live game, OS input, or network capture. The result is JSON-serializable so it
can be attached to a support bundle and uploaded for analysis.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import importlib
import platform
import sys
from typing import Callable


@dataclass
class CheckResult:
    name: str
    status: str
    message: str
    details: dict[str, object] = field(default_factory=dict)


@dataclass
class StartupReport:
    schema_version: str
    created_at_utc: str
    python: str
    platform: str
    checks: list[CheckResult]

    @property
    def ok(self) -> bool:
        return all(check.status in {"PASS", "WARN"} for check in self.checks)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["ok"] = self.ok
        return data


def _module_check(name: str, module: str) -> CheckResult:
    try:
        importlib.import_module(module)
        return CheckResult(name, "PASS", "module import succeeded", {"module": module})
    except Exception as exc:  # diagnostics must report, not crash
        return CheckResult(name, "FAIL", "module import failed", {"module": module, "error": repr(exc)})


def run_startup_checks(extra_checks: list[tuple[str, Callable[[], CheckResult]]] | None = None) -> StartupReport:
    checks = [
        _module_check("network_observation", "app.nostale_perception.network_observation"),
        _module_check("game_state", "app.nostale_perception.game_state"),
        _module_check("decoder_registry", "app.nostale_perception.network_decoder"),
        _module_check("skill_ledger", "app.nostale_perception.skill_ledger"),
        _module_check("autonomy_gateway", "app.nostale_perception.autonomy"),
        _module_check("simulation_executor", "app.nostale_perception.simulated_executor"),
    ]
    for name, check in extra_checks or []:
        try:
            checks.append(check())
        except Exception as exc:
            checks.append(CheckResult(name, "FAIL", "check crashed", {"error": repr(exc)}))
    return StartupReport(
        schema_version="nosai-startup-report-v1",
        created_at_utc=datetime.now(timezone.utc).isoformat(),
        python=sys.version,
        platform=platform.platform(),
        checks=checks,
    )
