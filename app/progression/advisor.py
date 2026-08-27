from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .models import CharacterSnapshot, PlanResult, ProgressionPlan
from .simulator import ProgressionSimulator

@dataclass(frozen=True)
class AdvisorReport:
    objective: str
    bottlenecks: tuple[str, ...]
    ranked: tuple[PlanResult, ...]
    recommendation: str | None
    status: str
    explanation: str

class ProgressionAdvisor:
    """GuardAi-side quantitative reviewer. Advisory only; no execution/payment."""
    def __init__(self, simulator: ProgressionSimulator | None = None) -> None:
        self.simulator = simulator or ProgressionSimulator()

    def analyze_bottlenecks(self, snapshot: CharacterSnapshot) -> tuple[str, ...]:
        out: list[str] = []
        if snapshot.resources.get("gold", 0.0) < 0: out.append("gold_data_invalid")
        if snapshot.derived.get("progression_score", 0.0) < 0.25: out.append("progression")
        if not snapshot.equipment: out.append("equipment_data_missing")
        if not snapshot.skills: out.append("skills_data_missing")
        return tuple(out)

    def evaluate(self, snapshot: CharacterSnapshot, objective: str, plans: Iterable[ProgressionPlan]) -> AdvisorReport:
        ranked = self.simulator.evaluate(snapshot, plans)
        usable = tuple(x for x in ranked if x.status != "BLOCKED_BY_POLICY")
        if not usable:
            return AdvisorReport(objective, self.analyze_bottlenecks(snapshot), ranked, None, "INSUFFICIENT_DATA", "Nessun piano utilizzabile dopo i controlli di policy.")
        top = usable[0]
        status = top.status
        explanation = f"GuardAi classifica {top.plan_id} come piano principale: utility={top.utility:.3f}, probabilità di successo={top.success_probability:.1%}, tempo mediano={top.p50_time_s:.0f}s."
        return AdvisorReport(objective, self.analyze_bottlenecks(snapshot), ranked, top.plan_id, status, explanation)

    @staticmethod
    def dashboard_payload(report: AdvisorReport) -> dict[str, Any]:
        return {"agent": "GuardAi", "objective": report.objective, "bottlenecks": list(report.bottlenecks), "recommendation": report.recommendation, "status": report.status, "explanation": report.explanation, "plans": [{"plan_id": r.plan_id, "expected_progress": r.expected_progress, "success_probability": r.success_probability, "expected_time_s": r.expected_time_s, "p50_time_s": r.p50_time_s, "p90_time_s": r.p90_time_s, "resource_cost": r.resource_cost, "risk": r.risk, "confidence": r.confidence, "utility": r.utility, "status": r.status, "reasons": list(r.reasons)} for r in report.ranked]}
