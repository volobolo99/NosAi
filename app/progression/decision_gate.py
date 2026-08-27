"""GuardAi recommendation gate for the control plane.

This adapter converts an advisory progression report into a control-plane decision
without granting execution authority. It intentionally has no side effects.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from app.control_plane.contracts import RunState
from .advisor import AdvisorReport


@dataclass(frozen=True)
class GuardAiDecision:
    status: str
    run_state: RunState
    recommendation: str | None
    execution_authorized: bool
    reason: str
    evidence: Mapping[str, Any]


def adjudicate(report: AdvisorReport) -> GuardAiDecision:
    if report.status in {"BLOCKED_BY_POLICY", "NOT_RECOMMENDED"}:
        return GuardAiDecision(report.status, RunState.BLOCKED, report.recommendation, False, report.explanation, {"agent": "GuardAi"})
    if report.status == "INSUFFICIENT_DATA":
        return GuardAiDecision(report.status, RunState.BLOCKED, None, False, report.explanation, {"agent": "GuardAi"})
    return GuardAiDecision(report.status, RunState.EVALUATING, report.recommendation, False, report.explanation, {"agent": "GuardAi"})
