"""Evidence-driven error research and isolated simulation pipeline.

The package never applies a candidate automatically. It records evidence,
tracks research provenance, and evaluates candidates in an isolated runner.
"""
from .candidate_generator import CandidateProposal, generate_candidates
from .engine import SimulationRepairEngine
from .models import CandidateResult, ErrorEvent, ResearchSource, SimulationRun
from .research import GitHubResearchProvider, ResearchError, ResearchHit, build_research_queries

__all__ = [
    "CandidateProposal",
    "CandidateResult",
    "ErrorEvent",
    "GitHubResearchProvider",
    "ResearchError",
    "ResearchHit",
    "ResearchSource",
    "SimulationRepairEngine",
    "SimulationRun",
    "build_research_queries",
    "generate_candidates",
]
