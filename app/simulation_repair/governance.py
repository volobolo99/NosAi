"""Promotion governance for research, simulation and real-runtime evidence.

A candidate can be promoted only when every required gate is explicitly PASS.
This module is deliberately policy-only: it never writes production files.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping


class GateStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_RUN = "NOT_RUN"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True, slots=True)
class GateResult:
    name: str
    status: GateStatus
    evidence_ids: tuple[str, ...] = ()
    detail: str = ""


@dataclass(frozen=True, slots=True)
class PromotionDecision:
    allowed: bool
    state: str
    blocking_gates: tuple[str, ...]
    gates: tuple[GateResult, ...]
    reason: str


REQUIRED_GATES = (
    "unit_tests",
    "integration_tests",
    "simulation_replay",
    "protected_regression",
    "static_analysis",
    "provenance",
    "real_windows",
    "real_nostale",
    "explicit_confirmation",
)


class PromotionFirewall:
    """Pure decision engine; production mutation is intentionally out of scope."""

    def evaluate(self, results: Mapping[str, GateResult], *, explicit_confirmation: bool = False) -> PromotionDecision:
        gates: list[GateResult] = []
        for name in REQUIRED_GATES:
            if name == "explicit_confirmation":
                status = GateStatus.PASS if explicit_confirmation else GateStatus.NOT_RUN
                gates.append(GateResult(name, status, detail="Human confirmation is required."))
            else:
                gates.append(results.get(name, GateResult(name, GateStatus.NOT_RUN)))
        blocking = tuple(g.name for g in gates if g.status != GateStatus.PASS)
        if blocking:
            return PromotionDecision(False, "BLOCKED", blocking, tuple(gates), "One or more required gates are not PASS.")
        return PromotionDecision(True, "READY_FOR_PROMOTION", (), tuple(gates), "All required gates passed and explicit confirmation was recorded.")
