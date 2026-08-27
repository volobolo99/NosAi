"""Orchestration layer for research and isolated candidate evaluation.

This module deliberately stops before automatic code changes. External research
is represented as injected sources so production credentials, network policy,
and provider choice stay outside the core engine.
"""
from __future__ import annotations

import hashlib
from dataclasses import replace
from typing import Any, Callable, Iterable

from .models import CandidateResult, ErrorEvent, ResearchSource, SimulationRun, utc_now

Researcher = Callable[[ErrorEvent], Iterable[ResearchSource]]
Simulator = Callable[[ErrorEvent, CandidateResult], dict[str, Any]]


class SimulationRepairEngine:
    """Deterministic coordinator for error -> research -> simulation evidence."""

    def __init__(self, researcher: Researcher | None = None, simulator: Simulator | None = None) -> None:
        self.researcher = researcher
        self.simulator = simulator
        self.runs: dict[str, SimulationRun] = {}

    @staticmethod
    def fingerprint(error: ErrorEvent) -> str:
        raw = "|".join((error.error_type, error.component, error.test_name, error.message, error.file or "", str(error.line or "")))
        return hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest()[:24]

    def register_error(self, error: ErrorEvent) -> SimulationRun:
        if not error.fingerprint:
            error.fingerprint = self.fingerprint(error)
        run = SimulationRun.create(error.error_id)
        self.runs[run.run_id] = run
        return run

    def research(self, run_id: str, error: ErrorEvent) -> SimulationRun:
        run = self._get(run_id)
        run.status, run.phase, run.progress_percent = "RUNNING", "research", 25
        if self.researcher is not None:
            run.research_sources = list(self.researcher(error))
        run.updated_at = utc_now()
        return run

    def evaluate(self, run_id: str, error: ErrorEvent, candidates: Iterable[CandidateResult]) -> SimulationRun:
        run = self._get(run_id)
        run.phase, run.progress_percent = "simulation", 50
        evaluated: list[CandidateResult] = []
        for candidate in candidates:
            if self.simulator is None:
                result = replace(candidate, status="NOT_RUN", notes=[*candidate.notes, "No simulator configured; candidate was not executed."])
            else:
                outcome = self.simulator(error, candidate)
                result = replace(
                    candidate,
                    status=outcome.get("status", "ERROR"),
                    evidence=[*candidate.evidence, *outcome.get("evidence", [])],
                    checks={**candidate.checks, **outcome.get("checks", {})},
                    notes=[*candidate.notes, *outcome.get("notes", [])],
                )
            evaluated.append(result)
        run.candidates = evaluated
        run.phase, run.progress_percent = "evidence", 90
        run.status = "READY_FOR_REVIEW" if evaluated and any(c.status == "PASS" for c in evaluated) else "FAIL"
        run.updated_at = utc_now()
        return run

    def seal(self, run_id: str) -> SimulationRun:
        run = self._get(run_id)
        run.phase, run.progress_percent, run.sealed = "sealed", 100, True
        run.updated_at = utc_now()
        return run

    def snapshot(self) -> dict[str, Any]:
        runs = [run.to_dict() for run in self.runs.values()]
        latest = runs[-1] if runs else None
        return {"runs": runs, "latest": latest, "count": len(runs)}

    def _get(self, run_id: str) -> SimulationRun:
        try:
            return self.runs[run_id]
        except KeyError as exc:
            raise KeyError(f"Unknown simulation run: {run_id}") from exc
