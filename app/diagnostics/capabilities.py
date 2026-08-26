"""Capability matrix built from deterministic health checks and runtime contracts."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .startup_check import CheckResult, StartupReport


class CapabilityStatus(str, Enum):
    READY = "READY"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Capability:
    name: str
    status: CapabilityStatus
    reason: str
    critical: bool = False


def build_capability_matrix(report: StartupReport, *, decode_ratio: float | None = None, benchmark_success_rate: float | None = None) -> list[Capability]:
    by_name = {check.name: check for check in report.checks}

    def module_ready(name: str) -> bool:
        return by_name.get(name, CheckResult(name, "FAIL", "missing check")).status == "PASS"

    capabilities = [
        Capability("network_observation", CapabilityStatus.READY if module_ready("network_observation") else CapabilityStatus.BLOCKED, "observation contract import", True),
        Capability("game_state", CapabilityStatus.READY if module_ready("game_state") else CapabilityStatus.BLOCKED, "state model import", True),
        Capability("decoder_registry", CapabilityStatus.READY if module_ready("decoder_registry") else CapabilityStatus.BLOCKED, "decoder infrastructure import", True),
        Capability("skill_ledger", CapabilityStatus.READY if module_ready("skill_ledger") else CapabilityStatus.BLOCKED, "skill verification storage", True),
        Capability("simulation", CapabilityStatus.READY if module_ready("simulation_executor") else CapabilityStatus.BLOCKED, "safe simulated execution", True),
    ]
    if decode_ratio is not None:
        status = CapabilityStatus.READY if decode_ratio >= 0.95 else CapabilityStatus.PARTIAL if decode_ratio >= 0.80 else CapabilityStatus.BLOCKED
        capabilities.append(Capability("decoder_coverage", status, f"decode_ratio={decode_ratio:.3f}", status == CapabilityStatus.BLOCKED))
    if benchmark_success_rate is not None:
        status = CapabilityStatus.READY if benchmark_success_rate >= 0.95 else CapabilityStatus.PARTIAL if benchmark_success_rate >= 0.80 else CapabilityStatus.BLOCKED
        capabilities.append(Capability("autonomy_benchmark", status, f"success_rate={benchmark_success_rate:.3f}", status == CapabilityStatus.BLOCKED))
    return capabilities


def autonomous_ready(capabilities: Iterable[Capability]) -> bool:
    caps = list(capabilities)
    return bool(caps) and all(c.status == CapabilityStatus.READY for c in caps if c.critical)
