from __future__ import annotations

from app.diagnostics.capabilities import CapabilityStatus, autonomous_ready, build_capability_matrix
from app.diagnostics.preflight import CheckResult, PreflightReport
from app.diagnostics.preflight_orchestrator import run_nosai_readiness


def _ready_report() -> PreflightReport:
    checks = tuple(
        CheckResult(f"check-{name}", "MODULE_IMPORT", "PASS", "INFO", "OK", "", "")
        for name in (
            "network_observation", "game_state", "decoder_registry", "skill_ledger", "simulation_executor"
        )
    )
    return PreflightReport("READY", checks)


def test_capability_matrix_is_blocked_by_missing_critical_capability() -> None:
    report = _ready_report()
    caps = build_capability_matrix(report, decode_ratio=0.5, benchmark_success_rate=0.9)
    assert any(c.status == CapabilityStatus.BLOCKED for c in caps)
    assert autonomous_ready(caps) is False


def test_unified_readiness_does_not_claim_autonomy_without_full_coverage() -> None:
    result = run_nosai_readiness(require_torch=False, modules=(), decode_ratio=1.0, benchmark_success_rate=1.0)
    assert result.autonomous_allowed is False
    assert result.preflight.passed is True
