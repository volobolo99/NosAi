"""End-to-end research -> proposal -> optional code-candidate orchestration."""
from __future__ import annotations

from dataclasses import dataclass

from .candidate_generator import CandidateProposal, generate_candidates
from .code_generation import CodeCandidate, CodeGenerationProvider, validate_candidate
from .models import ErrorEvent
from .research import MultiSourceResearchProvider, ResearchHit, build_research_queries


@dataclass(frozen=True)
class ResearchPipelineResult:
    queries: tuple[str, ...]
    hits: tuple[ResearchHit, ...]
    proposals: tuple[CandidateProposal, ...]
    code_candidates: tuple[CodeCandidate, ...]
    rejected_code_candidates: tuple[tuple[str, tuple[str, ...]], ...]


class ResearchPipeline:
    """Collect evidence and generate candidates without applying changes."""

    def __init__(self, researcher: MultiSourceResearchProvider | None = None, code_generator: CodeGenerationProvider | None = None) -> None:
        self.researcher = researcher or MultiSourceResearchProvider()
        self.code_generator = code_generator

    def run(self, error: ErrorEvent, *, max_sources: int = 16, max_proposals: int = 8) -> ResearchPipelineResult:
        queries = build_research_queries(error.error_type, error.message, error.component)
        hits = self.researcher.search(queries, total_limit=max_sources)
        proposals = generate_candidates(error.error_type, error.message, hits, limit=max_proposals)
        generated: list[CodeCandidate] = []
        rejected: list[tuple[str, tuple[str, ...]]] = []
        if self.code_generator is not None and proposals:
            for candidate in self.code_generator.generate(error_type=error.error_type, message=error.message, proposals=proposals):
                errors = tuple(validate_candidate(candidate))
                if errors:
                    rejected.append((candidate.candidate_id, errors))
                else:
                    generated.append(candidate)
        return ResearchPipelineResult(
            queries=tuple(queries),
            hits=tuple(hits),
            proposals=tuple(proposals),
            code_candidates=tuple(generated),
            rejected_code_candidates=tuple(rejected),
        )
