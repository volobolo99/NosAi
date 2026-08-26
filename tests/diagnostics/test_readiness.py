from __future__ import annotations

from types import SimpleNamespace

from app.diagnostics.decoder_coverage import DecoderCoverageReport
from app.diagnostics.readiness import evaluate_readiness
from app.diagnostics.replay_integrity import ReplayIntegrityReport


def _ready_preflight() -> SimpleNamespace:
    names = ["network_observation", "game_state", "decoder_registry", "skill_ledger", "simulation"]
    return SimpleNamespace(passed=True, checks=[SimpleNamespace(name=name, status="PASS") for name in names])


def test_autonomy_requires_all_evidence() -> None:
    integrity = ReplayIntegrityReport("fixture", total_lines=2, valid_observations=2)
    coverage = DecoderCoverageReport(2, 2, 0, 0, {"a": 2}, {})
    result = evaluate_readiness(_ready_preflight(), replay_integrity=integrity, decoder_coverage=coverage, benchmark_success_rate=1.0)
    assert result.autonomous_mode_allowed is True


def test_bad_fixture_blocks_autonomy() -> None:
    integrity = ReplayIntegrityReport("fixture", total_lines=1, valid_observations=0)
    integrity.issues.append(SimpleNamespace(code="INVALID_JSON"))
    coverage = DecoderCoverageReport(1, 1, 0, 0, {"a": 1}, {})
    result = evaluate_readiness(_ready_preflight(), replay_integrity=integrity, decoder_coverage=coverage, benchmark_success_rate=1.0)
    assert result.autonomous_mode_allowed is False
