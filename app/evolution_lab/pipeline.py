"""M3 orchestration: research -> candidates -> ensemble proposal."""
from __future__ import annotations

from dataclasses import dataclass

from .candidate_generation import generate_candidates
from .candidates import Candidate, CandidateEnsemble, compose_ensemble
from .providers import AggregatedResearch, ResearchProvider, aggregate_research


@dataclass(frozen=True, slots=True)
class EvolutionProposal:
    research: AggregatedResearch
    candidates: tuple[Candidate, ...]
    ensemble: CandidateEnsemble


def build_proposal(query: str, providers: list[ResearchProvider], *, limit: int = 10) -> EvolutionProposal:
    research = aggregate_research(query, providers, limit=limit)
    candidates = generate_candidates(research.findings)
    if not candidates:
        raise ValueError("research produced no candidates")
    ensemble = compose_ensemble(candidates)
    return EvolutionProposal(research, candidates, ensemble)
