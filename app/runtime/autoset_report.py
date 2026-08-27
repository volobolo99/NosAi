"""Serializable dashboard state for the hardware/AI AutoSet panel."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class AutoSetReport:
    status: str
    recommended_model: str
    hardware: dict[str, Any]
    benchmarks: list[dict[str, Any]]
    live_actions_enabled: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_report(recommended_model: str, hardware: dict[str, Any], benchmarks: list[dict[str, Any]]) -> dict[str, Any]:
    return AutoSetReport("ready", recommended_model, hardware, benchmarks, False).to_dict()
