from __future__ import annotations

from app.diagnostics.decoder_coverage import DecoderCoverageReport
from app.diagnostics.readiness import evaluate_readiness
from app.diagnostics.replay_integrity import ReplayIntegrityReport


class ReadyPreflight:
    passed = True
    checks = []


def test_autonomy_requires_all_evidence() -> None:
    integrity = ReplayIntegrityReport("fixture", total_lines=2, valid_observations=2)
    coverage = DecoderCoverageReport(2, 2, 0, 0, {"a": 2}, {})
    result = evaluate_readiness(ReadyPreflight(), replay_integrity=integrity, decoder_coverage=coverage, benchmark_success_rate=1.0)
    assert result.autonomous_mode_allowed is False


def test_bad_fixture_blocks_autonomy() -> None:
    integrity = ReplayIntegrityReport("fixture", total_lines=1, valid_observations=0, issues=[])
    integrity.issues.append(type("Issue", (), {"code": "INVALID_JSON"})())
    coverage = DecoderCoverageReport(1, 1, 0, 0, {"a": 1}, {})
    result = evaluate_readiness(ReadyPreflight(), replay_integrity=integrity, decoder_coverage=coverage, benchmark_success_rate=1.0)
    assert result.autonomous_mode_allowed is False
