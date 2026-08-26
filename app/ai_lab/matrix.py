from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any

from app.ai.brain import NosAiBrain

from .runner import ScenarioRun, run_scenario


@dataclass(frozen=True)
class MatrixSummary:
    total: int
    passed: int
    failed: int
    safety_failed: int

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0


def build_edge_case_matrix() -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    axes = product((0.12, 0.24, 0.50, 0.90), (0.08, 0.50, 0.90), (5.0, 12.0, 25.0), (0.0, 1.0), (10.0, 120.0))
    for index, (hp, mp, distance, resistance, time_left) in enumerate(axes):
        if hp < 0.25:
            expected, available, forbidden = "retreat", ["retreat", "heal", "attack", "move", "wait"], ["attack"]
        elif resistance >= 1.0:
            expected, available, forbidden = "move", ["move", "attack", "wait"], []
        else:
            expected, available, forbidden = "attack", ["attack", "move", "wait"], []
        scenarios.append({
            "scenario_id": f"matrix.edge_{index:03d}",
            "schema_version": 2,
            "source": "nosai_edge_matrix",
            "world_state": {"hp_ratio": hp, "mp_ratio": mp, "target_distance": distance, "target_resistance": resistance, "time_left_s": time_left, "objective": "raid"},
            "available_actions": available,
            "constraints": {"forbidden_actions": forbidden},
            "expected_decision": expected,
        })
    return scenarios


def run_edge_case_matrix(brain: NosAiBrain | None = None) -> tuple[list[ScenarioRun], MatrixSummary]:
    active = brain or NosAiBrain()
    runs = [run_scenario(active, scenario, candidate_id="nosai-brain-matrix") for scenario in build_edge_case_matrix()]
    summary = MatrixSummary(
        total=len(runs),
        passed=sum(run.result.status == "PASS" for run in runs),
        failed=sum(run.result.status == "FAIL" for run in runs),
        safety_failed=sum(run.result.safety_status == "FAIL" for run in runs),
    )
    return runs, summary
