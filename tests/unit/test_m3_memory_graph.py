from app.m3.memory_graph import MemoryGraph
from app.memory_v2.memory_manager import AIMemoryV2

def test_memory_graph_links_facts():
    g=MemoryGraph(); g.upsert_node("a","entity"); g.upsert_node("b","entity"); e=g.link("a","causes","b",.8)
    assert g.neighbors("a")[0] == e

def test_ai_memory_builds_graph():
    m=AIMemoryV2()
    m.ingest("MAP_CHANGED", {"map_id":"1","character_id":"hero"}, "test")
    assert m.graph.neighbors("character:hero", "located_at")
