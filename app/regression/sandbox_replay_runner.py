"""Deterministic candidate replay gate with fail-closed sandbox validation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from .anti_forgetting import verify_retention


class UnvalidatedCandidateError(RuntimeError):
    """Raised when a candidate cannot be validated in an isolated environment."""


@dataclass(frozen=True, slots=True)
class ReplayResult:
    candidate_id: str
    status: str
    replay_session_path: str
    decision_metrics: Mapping[str, float] = field(default_factory=dict)
    regressions: tuple[str, ...] = ()
    error: str | None = None


class SandboxReplayRunner:
    """Run deterministic candidate replay without touching the real client/hardware.

    This implementation intentionally requires an explicit sandbox marker in the
    replay session. It never silently falls back to the real runtime.
    """

    def __init__(self, *, max_degradation: float = 0.05) -> None:
        self.max_degradation = max_degradation

    def run_candidate_replay(
        self, candidate_id: str, replay_session_path: str
    ) -> ReplayResult:
        path = Path(replay_session_path)
        if not path.is_file():
            raise UnvalidatedCandidateError(f"replay session unavailable: {path}")

        try:
            payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise UnvalidatedCandidateError(f"invalid replay session: {path}") from exc

        if payload.get("sandbox_available") is not True:
            raise UnvalidatedCandidateError(
                "isolated sandbox is unavailable; candidate remains UNVALIDATED"
            )

        baseline = self._numeric_metrics(payload.get("baseline_metrics", {}))
        current = self._numeric_metrics(payload.get("candidate_metrics", {}))
        retained = verify_retention(current, baseline, self.max_degradation)
        status = "PASS" if retained else "FAIL"
        regressions = tuple(
            key for key in baseline if key in current and current[key] < baseline[key]
        )
        return ReplayResult(
            candidate_id=candidate_id,
            status=status,
            replay_session_path=str(path),
            decision_metrics=current,
            regressions=regressions,
        )

    @staticmethod
    def _numeric_metrics(value: Any) -> dict[str, float]:
        if not isinstance(value, Mapping):
            raise UnvalidatedCandidateError("replay metrics must be a mapping")
        result: dict[str, float] = {}
        for key, metric in value.items():
            if not isinstance(key, str) or not isinstance(metric, (int, float)):
                raise UnvalidatedCandidateError("replay metrics must be numeric")
            result[key] = float(metric)
        return result
