"""Capability matrix derived from deterministic diagnostics and benchmark evidence."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Any


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


def _check_status(report: Any, name: str) -> str:
    for check in getattr(report, "checks", ()):
        check_name = getattr(check, "name", None) or getattr(check, "check_id", None)
        if check_name == name or name in str(check_name):
            return str(getattr(check, "status", "FAIL"))
    return "FAIL"


def build_capability_matrix(
    report: Any,
    *,
    fixture_integrity_ok: bool | None = None,
    decode_ratio: float | None = None,
    benchmark_success_rate: float | None = None,
) -> list[Capability]:
    def module_ready(name: str) -> bool:
        return _check_status(report, name) == "PASS"

    capabilities = [
        Capability("network_observation", CapabilityStatus.READY if module_ready("network_observation") else CapabilityStatus.BLOCKED, "observation contract", True),
        Capability("game_state", CapabilityStatus.READY if module_ready("game_state") else CapabilityStatus.BLOCKED, "state model", True),
        Capability("decoder_registry", CapabilityStatus.READY if module_ready("decoder_registry") else CapabilityStatus.BLOCKED, "decoder infrastructure", True),
        Capability("skill_ledger", CapabilityStatus.READY if module_ready("skill_ledger") else CapabilityStatus.BLOCKED, "skill verification", True),
        Capability("simulation", CapabilityStatus.READY if module_ready("simulation_executor") else CapabilityStatus.BLOCKED, "safe simulation", True),
    ]
    if fixture_integrity_ok is not None:
        capabilities.append(Capability("replay_integrity", CapabilityStatus.READY if fixture_integrity_ok else CapabilityStatus.BLOCKED, "fixture/replay evidence integrity", True))
    if decode_ratio is not None:
        status = CapabilityStatus.READY if decode_ratio >= 0.95 else CapabilityStatus.PARTIAL if decode_ratio >= 0.80 else CapabilityStatus.BLOCKED
        capabilities.append(Capability("decoder_coverage", status, f"decode_ratio={decode_ratio:.3f}", True))
    if benchmark_success_rate is not None:
        status = CapabilityStatus.READY if benchmark_success_rate >= 0.95 else CapabilityStatus.PARTIAL if benchmark_success_rate >= 0.80 else CapabilityStatus.BLOCKED
        capabilities.append(Capability("autonomy_benchmark", status, f"success_rate={benchmark_success_rate:.3f}", True))
    return capabilities


def autonomous_ready(capabilities: Iterable[Capability]) -> bool:
    critical = [c for c in capabilities if c.critical]
    return bool(critical) and all(c.status == CapabilityStatus.READY for c in critical)
