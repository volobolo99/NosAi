"""NosAi v5 neuro-cognitive architecture.

Biological labels are a design metaphor; public APIs remain technical and
implementation-oriented. v5 composes perception, event routing, world state,
memory, value, planning, action selection, execution and consolidation without
coupling cognition to a specific game/client transport.
"""

from .core import (
    ActionCandidate,
    CognitiveCycle,
    CognitiveState,
    ExecutiveController,
    Observation,
    SafetyDecision,
    ValueAssessment,
)
from .consolidation import ConsolidationCandidate, ConsolidationPipeline
from .event_gateway import EventGateway, RoutedObservation
from .memory import EpisodicMemory, Episode, KnowledgeRecord
from .strategy_engine import Strategy, StrategyEngine, StrategyScore
from .world_state import WorldState

__all__ = [
    "ActionCandidate",
    "CognitiveCycle",
    "CognitiveState",
    "ConsolidationCandidate",
    "ConsolidationPipeline",
    "Episode",
    "EpisodicMemory",
    "EventGateway",
    "ExecutiveController",
    "KnowledgeRecord",
    "Observation",
    "RoutedObservation",
    "SafetyDecision",
    "Strategy",
    "StrategyEngine",
    "StrategyScore",
    "ValueAssessment",
    "WorldState",
]
