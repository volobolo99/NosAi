"""Machine-readable evaluation report and quality gates."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .evaluation import PerceptionEvaluation


@dataclass(frozen=True)
class QualityGate:
    max_hp_mae: float = 5.0
    max_mp_mae: float = 5.0
    max_position_mae: float = 1.0
    min_map_accuracy: float = 0.95


def gate_evaluation(result: PerceptionEvaluation, gate: QualityGate) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if result.hp.mae is not None and result.hp.mae > gate.max_hp_mae:
        failures.append("hp_mae")
    if result.mp.mae is not None and result.mp.mae > gate.max_mp_mae:
        failures.append("mp_mae")
    for name, metric in (("player_x_mae", result.player_x), ("player_y_mae", result.player_y)):
        if metric.mae is not None and metric.mae > gate.max_position_mae:
            failures.append(name)
    if result.map_accuracy is not None and result.map_accuracy < gate.min_map_accuracy:
        failures.append("map_accuracy")
    return not failures, failures


def write_report(path: str | Path, result: PerceptionEvaluation, gate: QualityGate) -> bool:
    passed, failures = gate_evaluation(result, gate)
    payload = {"passed": passed, "failures": failures, "gate": asdict(gate), "metrics": asdict(result)}
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return passed
