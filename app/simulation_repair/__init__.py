"""Evidence-driven error research and isolated simulation pipeline.

The package never applies a candidate automatically. It records evidence,
tracks research provenance, and evaluates candidates in an isolated runner.
"""
from .models import CandidateResult, ErrorEvent, ResearchSource, SimulationRun
from .engine import SimulationRepairEngine

__all__ = ["CandidateResult", "ErrorEvent", "ResearchSource", "SimulationRun", "SimulationRepairEngine"]
