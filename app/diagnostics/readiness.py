"""Combine pre-flight, replay integrity, decoder coverage, GameState and benchmark evidence."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .capabilities import Capability, autonomous_ready, build_capability_matrix
from .decoder_coverage import DecoderCoverageReport
from .replay_integrity import ReplayIntegrityReport
from app.nostale_perception.state_invariants import StateValidation


@dataclass(frozen=True)
class ReadinessResult:
    capabilities: tuple[Capability, ...]
    autonomous_mode_allowed: bool
    reason: str


def evaluate_readiness(
    preflight_report: Any,
    *,
    replay_integrity: ReplayIntegrityReport | None = None,
    decoder_coverage: DecoderCoverageReport | None = None,
    game_state_validation: StateValidation | None = None,
    benchmark_success_rate: float | None = None,
) -> ReadinessResult:
    capabilities = build_capability_matrix(
        preflight_report,
        fixture_integrity_ok=replay_integrity.ok if replay_integrity is not None else None,
        decode_ratio=decoder_coverage.decode_ratio if decoder_coverage is not None else None,
        game_state_valid=game_state_validation.valid if game_state_validation is not None else None,
        benchmark_success_rate=benchmark_success_rate,
    )
    evidence_present = (
        replay_integrity is not None
        and decoder_coverage is not None
        and game_state_validation is not None
        and benchmark_success_rate is not None
    )
    blocked = [c for c in capabilities if c.critical and c.status.value != "READY"]
    allowed = bool(getattr(preflight_report, "passed", False)) and evidence_present and autonomous_ready(capabilities)
    if not evidence_present:
        reason = "BLOCKED: required readiness evidence is missing"
    elif blocked:
        reason = "BLOCKED: " + "; ".join(f"{c.name}={c.reason}" for c in blocked)
    else:
        reason = "READY"
    return ReadinessResult(tuple(capabilities), allowed, reason)
