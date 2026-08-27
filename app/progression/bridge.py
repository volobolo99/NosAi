"""Bridge between PlayAi goal proposals and GuardAi evaluation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .advisor import ProgressionAdvisor, AdvisorReport
from .models import CharacterSnapshot, ProgressionPlan


@dataclass(frozen=True)
class PlayAiProposal:
    objective: str
    plans: tuple[ProgressionPlan, ...]
    rationale: str = ""


class PlayAiGuardAiBridge:
    """Side-effect-free PlayAi proposal -> GuardAi supervisory boundary."""

    def __init__(self, advisor: ProgressionAdvisor | None = None) -> None:
        self.advisor = advisor or ProgressionAdvisor()

    def evaluate(self, snapshot: CharacterSnapshot, proposal: PlayAiProposal) -> dict[str, Any]:
        errors = snapshot.validate()
        if errors:
            return {
                "producer": "PlayAi", "supervisor": "GuardAi",
                "objective": proposal.objective,
                "evaluation": None,
                "status": "BLOCKED",
                "validation_errors": list(errors),
                "execution_authorized": False,
            }
        report: AdvisorReport = self.advisor.evaluate(snapshot, proposal.objective, proposal.plans)
        return {
            "producer": "PlayAi", "supervisor": "GuardAi",
            "objective": proposal.objective,
            "proposal_rationale": proposal.rationale,
            "evaluation": self.advisor.dashboard_payload(report),
            "execution_authorized": False,
        }

    def evaluate_plans(self, snapshot: CharacterSnapshot, objective: str,
                       plans: Iterable[ProgressionPlan]) -> dict[str, Any]:
        return self.evaluate(snapshot, PlayAiProposal(objective, tuple(plans)))
