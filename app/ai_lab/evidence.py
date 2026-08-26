from __future__ import annotations

from typing import Any

from .runner import ScenarioRun


def scenario_evidence(run: ScenarioRun) -> dict[str, Any]:
    return {
        "scenario_id": run.result.scenario_id,
        "candidate_id": run.result.candidate_id,
        "decision": run.result.decision,
        "confidence": run.result.confidence,
        "evaluation_status": run.result.status,
        "safety_status": run.oracle.safety_status,
        "oracle_status": run.oracle.status,
        "reason_codes": list(run.oracle.reason_codes),
        "world_state": dict(run.world_state),
    }


def baseline_evidence(runs: tuple[ScenarioRun, ...]) -> list[dict[str, Any]]:
    return [scenario_evidence(run) for run in runs]
