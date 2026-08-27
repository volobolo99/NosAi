"""Bridge between PlayAi goal proposals and GuardAi evaluation.

The bridge is deliberately side-effect free: it converts a read-only world/character
snapshot into candidate plans and asks GuardAi to rank them. Execution is outside
this module and remains behind the existing execution/safety gates.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .advisor import GuardAiProgressionAdvisor
from .models import CharacterSnapshot, ProgressionPlan


@dataclass(frozen=True)
class PlayAiProposal:
    objective: str
    plans: tuple[ProgressionPlan, ...]
    rationale: str = ""


class PlayAiGuardAiBridge:
    """Cooperative proposal/evaluation boundary for the two AIs."""

    def __init__(self, advisor: GuardAiProgressionAdvisor | None = None) -> None:
        self.advisor = advisor or GuardAiProgressionAdvisor()

    def evaluate(self, snapshot: CharacterSnapshot, proposal: PlayAiProposal) -> dict[str, Any]:
        result = self.advisor.evaluate(snapshot, proposal.plans)
        return {
            "producer": "PlayAi",
            "supervisor": "GuardAi",
            "objective": proposal.objective,
            "proposal_rationale": proposal.rationale,
            "evaluation": result,
            "execution_authorized": False,
        }

    def evaluate_plans(self, snapshot: CharacterSnapshot, objective: str,
                       plans: Iterable[ProgressionPlan]) -> dict[str, Any]:
        return self.evaluate(snapshot, PlayAiProposal(objective, tuple(plans)))
