from app.knowledge import Edge, Evidence, KnowledgeNode, KnowledgeStore, NodeType


def test_graph_round_trip_and_evidence(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    source = KnowledgeNode(
        id="source:nostale-research",
        type=NodeType.SOURCE,
        title="NosTale Research Project",
        confidence=1.0,
        properties={"kind": "public_reference"},
    )
    bug = KnowledgeNode(
        id="bug:example",
        type=NodeType.BUG,
        title="Example anomaly (unverified)",
        status="suspected",
        confidence=0.25,
        properties={"safe_to_reproduce": True},
        evidence=[Evidence(source_id=source.id, url="https://example.invalid", confidence=0.2)],
    )
    store.upsert_node(source)
    store.upsert_node(bug)
    store.upsert_edge(Edge("edge:1", bug.id, "SUPPORTED_BY", source.id, confidence=0.2))

    loaded = store.get_node(bug.id)
    assert loaded is not None
    assert loaded.type is NodeType.BUG
    assert loaded.evidence[0].source_id == source.id

    neighbors = store.neighbors(bug.id)
    assert neighbors[0][1].id == source.id
    assert neighbors[0][0].relation == "SUPPORTED_BY"


def test_search_and_export_import(tmp_path):
    first = KnowledgeStore(tmp_path / "first.sqlite3")
    first.upsert_node(KnowledgeNode("bug:movement", NodeType.BUG, "Movement anomaly", confidence=0.7))
    first.upsert_node(KnowledgeNode("packet:walk", NodeType.PACKET, "walk", confidence=0.9))
    first.upsert_edge(Edge("edge:movement-packet", "bug:movement", "INVOLVES", "packet:walk"))

    assert [n.id for n in first.search("movement")] == ["bug:movement"]
    assert first.search("", NodeType.PACKET)[0].id == "packet:walk"

    second = KnowledgeStore(tmp_path / "second.sqlite3")
    second.import_json(first.export_json())
    assert second.get_node("bug:movement") is not None
    assert second.neighbors("bug:movement")[0][1].id == "packet:walk"
