"""Orchestration for research, sandbox evaluation and multi-candidate synthesis."""
from __future__ import annotations

import hashlib
from dataclasses import replace
from typing import Any, Callable, Iterable

from .candidate_generator import generate_candidates
from .ensemble import EnsembleResult, synthesize
from .models import CandidateResult, ErrorEvent, ResearchSource, SimulationRun, utc_now
from .research import GitHubResearchProvider, build_research_queries
from .research_pipeline import ResearchPipeline, ResearchPipelineResult

Researcher = Callable[[ErrorEvent], Iterable[ResearchSource]]
Simulator = Callable[[ErrorEvent, CandidateResult], dict[str, Any]]


class SimulationRepairEngine:
    """Deterministic coordinator; never applies production code changes."""

    def __init__(self, researcher: Researcher | None = None, simulator: Simulator | None = None, github_research: GitHubResearchProvider | None = None, research_pipeline: ResearchPipeline | None = None) -> None:
        self.researcher = researcher
        self.simulator = simulator
        self.github_research = github_research or GitHubResearchProvider()
        self.research_pipeline = research_pipeline
        self.runs: dict[str, SimulationRun] = {}
        self.ensembles: dict[str, EnsembleResult] = {}

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

    def research_online_and_generate(self, run_id: str, error: ErrorEvent, *, limit_per_query: int = 6, candidate_limit: int = 12) -> list[CandidateResult]:
        """Search live GitHub and turn evidence into traceable proposals."""
        run = self._get(run_id)
        run.status, run.phase, run.progress_percent = "RUNNING", "online_research", 20
        hits = []
        for query in build_research_queries(error.error_type, error.message, error.component):
            hits.extend(self.github_research.search(query, limit=limit_per_query))
        dedup = {hit.url: hit for hit in hits if hit.url}
        run.research_sources = [ResearchSource(title=hit.title, url=hit.url, source_type=hit.source_type) for hit in dedup.values()]
        proposals = generate_candidates(error.error_type, error.message, dedup.values(), limit=candidate_limit)
        candidates = [
            CandidateResult(
                candidate_id=p.candidate_id,
                status="QUEUED",
                description=p.description,
                evidence=list(p.evidence_urls),
                source_ids=[url for url in p.evidence_urls],
                notes=[f"strategy={p.strategy}", "proposal-only; no source code was executed"],
            )
            for p in proposals
        ]
        run.candidates = candidates
        run.phase, run.progress_percent = "candidate_generation", 40
        run.updated_at = utc_now()
        return candidates

    def research_and_generate(self, error: ErrorEvent, *, max_sources: int = 16, max_proposals: int = 8) -> ResearchPipelineResult:
        """Run multi-source research plus optional structured code generation."""
        if self.research_pipeline is None:
            raise RuntimeError("No ResearchPipeline configured")
        return self.research_pipeline.run(error, max_sources=max_sources, max_proposals=max_proposals)

    def evaluate(self, run_id: str, error: ErrorEvent, candidates: Iterable[CandidateResult]) -> SimulationRun:
        run = self._get(run_id)
        run.phase, run.progress_percent = "simulation", 50
        evaluated: list[CandidateResult] = []
        for candidate in candidates:
            if self.simulator is None:
                result = replace(candidate, status="NOT_RUN", notes=[*candidate.notes, "No simulator configured; candidate was not executed."])
            else:
                outcome = self.simulator(error, candidate)
                result = replace(candidate, status=outcome.get("status", "ERROR"), evidence=[*candidate.evidence, *outcome.get("evidence", [])], checks={**candidate.checks, **outcome.get("checks", {})}, notes=[*candidate.notes, *outcome.get("notes", [])])
            evaluated.append(result)
        run.candidates = evaluated
        run.phase, run.progress_percent = "ensemble", 85
        self.ensembles[run_id] = synthesize(evaluated)
        run.phase, run.progress_percent = "evidence", 90
        run.status = "READY_FOR_REVIEW" if self.ensembles[run_id].status in {"READY_FOR_REVIEW", "CONFLICT_REVIEW"} else "FAIL"
        run.updated_at = utc_now()
        return run

    def seal(self, run_id: str) -> SimulationRun:
        run = self._get(run_id)
        run.phase, run.progress_percent, run.sealed = "sealed", 100, True
        run.updated_at = utc_now()
        return run

    def snapshot(self) -> dict[str, Any]:
        runs = []
        for run in self.runs.values():
            item = run.to_dict()
            ensemble = self.ensembles.get(run.run_id)
            if ensemble:
                item["ensemble"] = {
                    "status": ensemble.status,
                    "selected_candidate_ids": ensemble.selected_candidate_ids,
                    "compatible_candidate_ids": ensemble.compatible_candidate_ids,
                    "composite_plan": ensemble.composite_plan,
                    "conflicts": ensemble.conflicts,
                    "score": ensemble.score,
                }
            runs.append(item)
        return {"runs": runs, "latest": runs[-1] if runs else None, "count": len(runs)}

    def _get(self, run_id: str) -> SimulationRun:
        try:
            return self.runs[run_id]
        except KeyError as exc:
            raise KeyError(f"Unknown simulation run: {run_id}") from exc
