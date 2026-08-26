"""Graph orchestration for normalized evidence."""
from __future__ import annotations

from .models import Edge, KnowledgeNode
from .normalizer import KnowledgeNormalizer
from .store import KnowledgeStore


class KnowledgeGraphBuilder:
    def __init__(self, store: KnowledgeStore) -> None:
        self.store = store
        self.normalizer = KnowledgeNormalizer(store)

    def ingest_source(self, source: KnowledgeNode) -> list[KnowledgeNode]:
        """Persist a source and derive conservative entities from its evidence."""
        self.store.upsert_node(source)
        return self.normalizer.normalize_source(source)

    def link_extracted_nodes(self, nodes: list[KnowledgeNode]) -> int:
        """Create safe semantic links among entities extracted from one evidence set."""
        count = 0
        anomalies = [n for n in nodes if n.type.name in {"BUG", "GLITCH", "ANOMALY"}]
        packets = [n for n in nodes if n.type.name == "PACKET"]
        versions = [n for n in nodes if n.type.name == "VERSION"]
        for anomaly in anomalies:
            for packet in packets:
                self.store.upsert_edge(Edge(
                    id=f"edge:{anomaly.id}:INVOLVES:{packet.id}",
                    source_id=anomaly.id, relation="INVOLVES", target_id=packet.id,
                    confidence=min(anomaly.confidence, packet.confidence),
                ))
                count += 1
            for version in versions:
                self.store.upsert_edge(Edge(
                    id=f"edge:{anomaly.id}:OBSERVED_IN:{version.id}",
                    source_id=anomaly.id, relation="OBSERVED_IN", target_id=version.id,
                    confidence=min(anomaly.confidence, version.confidence),
                ))
                count += 1
        return count

    def ingest_and_link(self, source: KnowledgeNode) -> tuple[list[KnowledgeNode], int]:
        nodes = self.ingest_source(source)
        return nodes, self.link_extracted_nodes(nodes)
