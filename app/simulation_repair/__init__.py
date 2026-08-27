"""Evidence-driven error research and isolated simulation pipeline.

The package never applies a candidate automatically. It records evidence,
tracks research provenance, evaluates candidates in an isolated runner, and
keeps promotion/replay/registry governance explicit.
"""
from .candidate_generator import CandidateProposal, generate_candidates
from .code_generation import CodeCandidate, CodeGenerationProvider, validate_candidate
from .engine import SimulationRepairEngine
from .governance import GateResult, GateStatus, PromotionDecision, PromotionFirewall
from .models import CandidateResult, ErrorEvent, ResearchSource, SimulationRun
from .replay import ReplayCase, ReplayStore, anti_forgetting_gate
from .registry import RegistryEntry, VersionRegistry
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
    "GateResult",
    "GateStatus",
    "GitHubResearchProvider",
    "MultiSourceResearchProvider",
    "PromotionDecision",
    "PromotionFirewall",
    "RegistryEntry",
    "ReplayCase",
    "ReplayStore",
    "ResearchError",
    "ResearchHit",
    "ResearchPipeline",
    "ResearchPipelineResult",
    "ResearchSource",
    "SimulationRepairEngine",
    "SimulationRun",
    "StackOverflowResearchProvider",
    "VersionRegistry",
    "anti_forgetting_gate",
    "build_research_queries",
    "generate_candidates",
    "validate_candidate",
]
