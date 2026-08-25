from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Any

@dataclass(frozen=True)
class MemoryNode:
    node_id: str
    kind: str
    attributes: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class MemoryEdge:
    source: str
    relation: str
    target: str
    confidence: float = 1.0

class MemoryGraph:
    """Lightweight indexed graph over durable memory facts and causal links."""
    def __init__(self):
        self.nodes: dict[str, MemoryNode] = {}
        self.edges: list[MemoryEdge] = []
        self._out: dict[str, list[MemoryEdge]] = defaultdict(list)

    def upsert_node(self, node_id: str, kind: str, **attributes) -> MemoryNode:
        node = MemoryNode(node_id, kind, dict(attributes))
        self.nodes[node_id] = node
        return node

    def link(self, source: str, relation: str, target: str, confidence: float = 1.0) -> MemoryEdge:
        if source not in self.nodes or target not in self.nodes:
            raise KeyError("both graph nodes must exist before linking")
        edge = MemoryEdge(source, relation, target, max(0.0, min(1.0, float(confidence))))
        self.edges.append(edge)
        self._out[source].append(edge)
        return edge

    def neighbors(self, node_id: str, relation: str | None = None) -> list[MemoryEdge]:
        edges = self._out.get(node_id, [])
        return [e for e in edges if relation is None or e.relation == relation]

    def from_fact(self, fact) -> None:
        self.upsert_node(fact.subject, "entity")
        target = str(fact.object)
        self.upsert_node(target, "entity")
        self.link(fact.subject, fact.predicate, target, fact.confidence)
