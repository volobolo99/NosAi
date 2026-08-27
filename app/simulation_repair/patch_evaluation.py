"""Pure evaluation rules for candidate patches.

This module scores evidence; it does not execute patches or mutate a checkout.
"""
from __future__ import annotations

from dataclasses import dataclass

from .sandbox import SandboxResult


@dataclass(frozen=True, slots=True)
class PatchEvaluation:
    candidate_id: str
    status: str
    replay_passed: bool
    regression_passed: bool
    anti_forgetting_passed: bool
    detail: str


def evaluate_patch(
    candidate_id: str,
    sandbox: SandboxResult,
    *,
    replay_passed: bool,
    regression_passed: bool,
    anti_forgetting_passed: bool,
) -> PatchEvaluation:
    """Return PASS only when real isolation evidence and all gates pass."""
    if sandbox.status != "PASS":
        return PatchEvaluation(
            candidate_id,
            "FAIL",
            replay_passed,
            regression_passed,
            anti_forgetting_passed,
            f"Sandbox status is {sandbox.status}; candidate is not promotable.",
        )
    if sandbox.isolation in {"", "none", "unverified"}:
        return PatchEvaluation(
            candidate_id,
            "FAIL",
            replay_passed,
            regression_passed,
            anti_forgetting_passed,
            "Sandbox reported PASS without a verified isolation boundary; candidate is not promotable.",
        )
    if not replay_passed or not regression_passed or not anti_forgetting_passed:
        return PatchEvaluation(
            candidate_id,
            "FAIL",
            replay_passed,
            regression_passed,
            anti_forgetting_passed,
            "One or more replay/regression/anti-forgetting gates failed.",
        )
    return PatchEvaluation(
        candidate_id,
        "PASS",
        True,
        True,
        True,
        "Sandbox, replay, regression and anti-forgetting gates passed.",
    )
