
from app.memory_v2.memory_manager import AIMemoryV2


def test_observation_to_inference_pipeline():
    memory = AIMemoryV2()

    defeat = memory.ingest(
        "MONSTER_DEFEATED",
        {"monster_id": 500},
        "tcp",
        "session",
    )

    reward = memory.ingest(
        "ITEM_RECEIVED",
        {"item_id": 900},
        "tcp",
        "session",
    )

    # Use the actual event timestamps and derive the candidate relation.
    memory.consolidator.infer_item_source(
        [defeat, reward],
        window_seconds=10,
    )

    assert len(memory.store.inferences) == 1


def test_knowledge_consolidation_updates_unified_graph():
    from app.memory_v2.models import Inference, StrategyExperience
    memory = AIMemoryV2()
    memory.store.add_inference(Inference("i1", "monster:1", "probably_drops", "item:2", .9, ["o1", "o2"]))
    for _ in range(3):
        memory.store.add_strategy_experience(StrategyExperience("farm", "safe", True, 10, 2, .1, {}))
    result = memory.consolidate_knowledge()
    assert result["inferences"] and result["strategies"]
    assert any(e.source == "monster:1" and e.target == "item:2" for e in memory.graph.edges)
