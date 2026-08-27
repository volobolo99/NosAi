"""Evidence-driven error research and isolated simulation pipeline.

The package never applies a candidate automatically. It records evidence,
tracks research provenance, and evaluates candidates in an isolated runner.
"""
from .candidate_generator import CandidateProposal, generate_candidates
from .code_generation import CodeCandidate, CodeGenerationProvider, validate_candidate
from .engine import SimulationRepairEngine
from .models import CandidateResult, ErrorEvent, ResearchSource, SimulationRun
from .research import (
    GitHubResearchProvider,
    MultiSourceResearchProvider,
    ResearchError,
    ResearchHit,
    StackOverflowResearchProvider,
    build_research_queries,
)
from .research_pipeline import ResearchPipeline, ResearchPipelineResult

__all__ = [
    "CandidateProposal",
    "CandidateResult",
    "CodeCandidate",
    "CodeGenerationProvider",
    "ErrorEvent",
    "GitHubResearchProvider",
    "MultiSourceResearchProvider",
    "ResearchError",
    "ResearchHit",
    "ResearchPipeline",
    "ResearchPipelineResult",
    "ResearchSource",
    "SimulationRepairEngine",
    "SimulationRun",
    "StackOverflowResearchProvider",
    "build_research_queries",
    "generate_candidates",
    "validate_candidate",
]
