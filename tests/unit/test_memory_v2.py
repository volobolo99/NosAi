
from app.memory_v2.memory_manager import AIMemoryV2


def test_ingest_creates_observation_and_fact():
    memory = AIMemoryV2()

    memory.ingest(
        "MAP_CHANGED",
        {"character_id": 1, "map_id": 12},
        "tcp",
        session_id="s1",
    )

    assert len(memory.store.observations) == 1
    assert len(memory.store.facts) == 1

    results = memory.query("character located map")
    assert results


def test_recent_context():
    memory = AIMemoryV2()
    memory.ingest("ITEM_RECEIVED", {"item_id": 10}, "tcp", "s1")
    context = memory.context("s1")
    assert len(context["recent_observations"]) == 1


def test_strategy_learning():
    from app.memory_v2.models import StrategyExperience

    memory = AIMemoryV2()

    memory.strategy_learning.record(
        StrategyExperience("PVM", "safe", True, 10, 20, .1)
    )
    memory.strategy_learning.record(
        StrategyExperience("PVM", "fast", False, -5, 5, .8)
    )

    ranking = memory.strategy_learning.ranking("PVM")
    assert ranking[0]["strategy_id"] == "safe"


def test_repeated_inference_is_promoted_to_stable_fact():
    from app.memory_v2.models import Inference
    m = AIMemoryV2()
    m.store.add_inference(Inference("i1", "monster:1", "probably_drops", "item:2", .9, ["o1", "o2"]))
    promoted = m.consolidator.consolidate_inferences()
    assert promoted == ["monster:1|probably_drops|item:2"]
    assert m.store.facts["monster:1|probably_drops|item:2"].confidence == .9
    assert m.store.inferences["i1"].status == "confirmed"


def test_successful_strategy_is_promoted_to_semantic_knowledge():
    from app.memory_v2.models import StrategyExperience
    m = AIMemoryV2()
    for _ in range(3):
        m.store.add_strategy_experience(StrategyExperience("farm", "safe", True, 10, 2, .1, {}))
    promoted = m.consolidator.consolidate_strategy_knowledge()
    assert promoted == ["strategy:farm|preferred:safe"]
    assert m.store.facts["strategy:farm|preferred:safe"].predicate == "preferred_strategy"
