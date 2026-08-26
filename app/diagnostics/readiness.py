"""Combine pre-flight, replay integrity, decoder coverage and benchmark evidence."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .capabilities import Capability, autonomous_ready, build_capability_matrix
from .decoder_coverage import DecoderCoverageReport
from .replay_integrity import ReplayIntegrityReport


@dataclass(frozen=True)
class ReadinessResult:
    capabilities: tuple[Capability, ...]
    autonomous_mode_allowed: bool


def evaluate_readiness(
    preflight_report: Any,
    *,
    replay_integrity: ReplayIntegrityReport | None = None,
    decoder_coverage: DecoderCoverageReport | None = None,
    benchmark_success_rate: float | None = None,
) -> ReadinessResult:
    capabilities = build_capability_matrix(
        preflight_report,
        fixture_integrity_ok=replay_integrity.ok if replay_integrity is not None else None,
        decode_ratio=decoder_coverage.decode_ratio if decoder_coverage is not None else None,
        benchmark_success_rate=benchmark_success_rate,
    )
    # Real autonomy is deliberately not granted by module imports alone. Evidence
    # from replay integrity, decoder coverage and benchmark must be supplied first.
    evidence_present = replay_integrity is not None and decoder_coverage is not None and benchmark_success_rate is not None
    allowed = bool(getattr(preflight_report, "passed", False)) and evidence_present and autonomous_ready(capabilities)
    return ReadinessResult(tuple(capabilities), allowed)
