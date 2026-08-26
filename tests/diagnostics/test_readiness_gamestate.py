from __future__ import annotations

from dataclasses import dataclass

from app.diagnostics.decoder_coverage import DecoderCoverageReport
from app.diagnostics.readiness import evaluate_readiness
from app.diagnostics.replay_integrity import ReplayIntegrityReport
from app.nostale_perception.state_invariants import StateIssue, StateValidation


@dataclass(frozen=True)
class Check:
    name: str
    status: str


@dataclass(frozen=True)
class Report:
    checks: tuple[Check, ...]
    passed: bool = True


def _report() -> Report:
    return Report(tuple(Check(name, "PASS") for name in (
        "network_observation", "game_state", "decoder_registry", "skill_ledger", "simulation_executor",
    )))


def _evidence(state: StateValidation) -> dict:
    return dict(
        replay_integrity=ReplayIntegrityReport(path="fixture"),
        decoder_coverage=DecoderCoverageReport(100, 100, 0, 0, {"known": 100}, {}),
        game_state_validation=state,
        benchmark_success_rate=1.0,
    )


def test_invalid_game_state_blocks_autonomy() -> None:
    state = StateValidation((StateIssue("PLAYER_HP_OVER_MAX", "ERROR", "invalid"),))
    result = evaluate_readiness(_report(), **_evidence(state))
    assert result.autonomous_mode_allowed is False
    assert any(c.name == "game_state_integrity" and c.status.value == "BLOCKED" for c in result.capabilities)
    assert "game_state_integrity" in result.reason


def test_valid_game_state_allows_autonomy_when_all_other_evidence_is_ready() -> None:
    result = evaluate_readiness(_report(), **_evidence(StateValidation(())))
    assert result.autonomous_mode_allowed is True
    assert result.reason == "READY"


def test_missing_game_state_evidence_blocks_autonomy() -> None:
    evidence = _evidence(StateValidation(()))
    evidence.pop("game_state_validation")
    result = evaluate_readiness(_report(), **evidence)
    assert result.autonomous_mode_allowed is False
    assert "required readiness evidence" in result.reason
