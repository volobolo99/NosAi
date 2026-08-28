from app.cognition_v5 import EpisodicMemory, Episode, Observation
from app.cognition_v5.consolidation import ConsolidationPipeline
from app.cognition_v5.event_gateway import EventGateway
from app.cognition_v5.strategy_engine import Strategy, StrategyEngine
from app.cognition_v5.world_state import WorldState


def test_gateway_projects_observation_into_versioned_world_state() -> None:
    state = EventGateway().project(WorldState(), [Observation("hp_ratio", 0.8)])
    assert state.version == 2
    assert state.get("hp_ratio") == 0.8


def test_strategy_engine_uses_episode_evidence() -> None:
    memory = EpisodicMemory()
    for i in range(3):
        memory.append(Episode(str(i), "s", "farm", "farm_safe", "success", 10.0))
    engine = StrategyEngine(memory)
    ranked = engine.rank(
        [Strategy("farm_safe", "farm", base_value=1.0, risk=0.1, confidence=0.2)],
        WorldState(),
    )
    assert ranked[0].strategy_id == "farm_safe"
    assert ranked[0].evidence_count == 3
    assert ranked[0].confidence == 1.0


def test_consolidation_requires_repeated_high_confidence_evidence() -> None:
    episodes = [
        Episode(str(i), "s", "farm", "farm_safe", "success", 10.0) for i in range(3)
    ]
    pipeline = ConsolidationPipeline()
    candidates = pipeline.extract(episodes)
    record = pipeline.promote(candidates[0])
    assert record is not None
    assert record.evidence_count == 3
    assert record.confidence == 1.0
