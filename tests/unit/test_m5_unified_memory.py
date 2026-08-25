from app.memory_v2.memory_manager import AIMemoryV2
from app.m5 import UnifiedMemory
from app.memory_v2.models import MemoryFact, StrategyExperience


def test_unified_memory_normalizes_episodic_and_semantic():
    m = AIMemoryV2()
    obs = m.ingest("MAP_CHANGED", {"map_id": "a1"}, "game", session_id="s1", confidence=.9)
    assert any(x.record_id == obs.id and x.kind == "episodic" for x in m.unified.records())
    assert any(x.record.kind == "semantic" and x.record.attributes["object"] == "map:a1" for x in m.unified.retrieve("located map:a1"))


def test_goal_aware_retrieval_prefers_relevant_strategy():
    m = AIMemoryV2()
    m.store.add_strategy_experience(StrategyExperience("farm", "safe_route", True, 10.0, 4.0, .1, {"map": "a1"}))
    m.store.add_strategy_experience(StrategyExperience("boss", "burst", False, -5.0, 2.0, .9, {"map": "b2"}))
    hits = m.unified.retrieve(goal="farm", query="safe_route", kinds=["strategy"])
    assert hits and hits[0].record.attributes["strategy_id"] == "safe_route"


def test_graph_is_shared_and_idempotent():
    m = AIMemoryV2()
    m.ingest("ITEM_RECEIVED", {"item_id": "x"}, "game")
    edges = len(m.graph.edges)
    m.unified.consolidate_graph()
    assert len(m.graph.edges) == edges
    assert m.unified.graph is m.graph


def test_legacy_query_still_works():
    m = AIMemoryV2()
    m.ingest("MAP_CHANGED", {"map_id": "legacy"}, "game")
    assert m.query("located legacy")


def test_retrieval_uses_goal_context_and_confidence():
    m = AIMemoryV2()
    m.ingest("MAP_CHANGED", {"map_id": "farm_zone"}, "game", confidence=.95)
    m.store.add_strategy_experience(StrategyExperience("farm", "safe_route", True, 10.0, 4.0, .1, {"map": "farm_zone"}))
    m.store.add_strategy_experience(StrategyExperience("boss", "burst", True, 12.0, 3.0, .8, {"map": "farm_zone"}))
    hits = m.unified.retrieve(goal="farm", query="safe route", kinds=["strategy"])
    assert hits[0].record.attributes["strategy_id"] == "safe_route"


def test_retrieval_graph_expansion_finds_related_memory():
    m = AIMemoryV2()
    m.ingest("ITEM_RECEIVED", {"item_id": "sword"}, "game", confidence=.9)
    m.store.add_fact(MemoryFact("f1", "sword", "used_in", "raid", .95, []))
    m.unified.consolidate_graph()
    hits = m.unified.retrieve(query="raid", entity_ids=["sword"], kinds=["semantic"], graph_depth=1)
    assert hits and hits[0].record.attributes["subject"] == "sword"


def test_retrieval_filters_session_and_event_type():
    m = AIMemoryV2()
    m.ingest("MAP_CHANGED", {"map_id": "a"}, "game", session_id="s1")
    m.ingest("COMBAT", {"target": "boss"}, "game", session_id="s2")
    hits = m.unified.retrieve(query="COMBAT", event_types=["COMBAT"], session_id="s2")
    assert len(hits) == 1 and hits[0].record.attributes["session_id"] == "s2"
