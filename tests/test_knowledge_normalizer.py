from app.knowledge import Evidence, KnowledgeNode, KnowledgeStore, NodeType
from app.knowledge.graph_builder import KnowledgeGraphBuilder


def test_normalizer_extracts_anomaly_packet_and_version(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    source = KnowledgeNode(
        id="source:test", type=NodeType.SOURCE, title="test source", confidence=1.0,
        evidence=[Evidence(
            source_id="source:test",
            url="https://example.invalid/test",
            quote="Bug in packet walk on version 1.2.3 causes a movement anomaly.",
            version="1.2.3", confidence=0.9,
        )],
    )
    builder = KnowledgeGraphBuilder(store)
    nodes, links = builder.ingest_and_link(source)

    types = {node.type for node in nodes}
    assert NodeType.BUG in types or NodeType.ANOMALY in types
    assert NodeType.PACKET in types
    assert NodeType.VERSION in types
    assert links >= 2

    anomalies = [n for n in nodes if n.type in {NodeType.BUG, NodeType.ANOMALY}]
    neighbors = store.neighbors(anomalies[0].id)
    relations = {edge.relation for edge, _ in neighbors}
    assert "SUPPORTED_BY" in relations
    assert "INVOLVES" in relations
    assert "OBSERVED_IN" in relations


def test_unrelated_text_does_not_create_bug(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite3")
    source = KnowledgeNode(
        id="source:clean", type=NodeType.SOURCE, title="clean", confidence=1.0,
        evidence=[Evidence(source_id="source:clean", quote="Player walks through the map normally.", confidence=1.0)],
    )
    nodes = KnowledgeGraphBuilder(store).ingest_source(source)
    assert not any(n.type in {NodeType.BUG, NodeType.GLITCH, NodeType.ANOMALY} for n in nodes)
