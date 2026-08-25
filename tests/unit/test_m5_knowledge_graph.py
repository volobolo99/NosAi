from app.memory_v2.memory_manager import AIMemoryV2
from app.m5 import KnowledgeGraph


def test_typed_entities_and_provenance():
    g = KnowledgeGraph()
    g.upsert_entity("player", "agent", level=10)
    g.upsert_entity("map:a1", "map")
    e = g.relate("player", "located_on", "map:a1", confidence=.8, provenance=["obs:1"])
    assert e.confidence == .8
    assert e.provenance == ("obs:1",)
    assert g.entities["player"].entity_type == "agent"


def test_duplicate_relation_is_idempotent():
    g = KnowledgeGraph()
    g.upsert_entity("a")
    g.upsert_entity("b")
    first = g.relate("a", "knows", "b", confidence=.5)
    second = g.relate("a", "knows", "b", confidence=.9)
    assert first == second
    assert len(g.relations) == 1


def test_traversal_and_relation_filter():
    g = KnowledgeGraph()
    for x in ("a", "b", "c"):
        g.upsert_entity(x)
    g.relate("a", "leads_to", "b")
    g.relate("b", "leads_to", "c")
    g.relate("a", "other", "c")
    assert g.traverse("a", relation="leads_to", max_depth=2) == [("b", 1), ("c", 2)]


def test_build_from_unified_memory():
    m = AIMemoryV2()
    m.ingest("MAP_CHANGED", {"map_id": "a1"}, "game", confidence=.9)
    kg = KnowledgeGraph.from_unified_memory(m.unified)
    located = kg.query_relation("located_at")
    assert located
    assert located[0].provenance
