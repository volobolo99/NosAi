"""Single pre-flight entry point combining startup diagnostics and capability gating."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .capabilities import Capability, autonomous_ready, build_capability_matrix
from .preflight import CheckResult, PreflightReport, run_preflight


@dataclass(frozen=True)
class NosAiReadiness:
    preflight: PreflightReport
    capabilities: tuple[Capability, ...]
    autonomous_allowed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "preflight": self.preflight.to_dict(),
            "capabilities": [
                {"name": c.name, "status": c.status.value, "reason": c.reason, "critical": c.critical}
                for c in self.capabilities
            ],
            "autonomous_allowed": self.autonomous_allowed,
        }


def run_nosai_readiness(
    *,
    client_adapter: Any = None,
    modules: Iterable[str] | None = None,
    require_client: bool = False,
    require_torch: bool = True,
    decode_ratio: float | None = None,
    benchmark_success_rate: float | None = None,
) -> NosAiReadiness:
    report = run_preflight(
        client_adapter=client_adapter,
        modules=modules if modules is not None else (),
        require_client=require_client,
        require_torch=require_torch,
    )
    capabilities = tuple(build_capability_matrix(report, decode_ratio=decode_ratio, benchmark_success_rate=benchmark_success_rate))
    return NosAiReadiness(report, capabilities, report.passed and autonomous_ready(capabilities))
