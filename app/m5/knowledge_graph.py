from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict, deque
from typing import Any, Iterable


@dataclass(frozen=True)
class KnowledgeEntity:
    entity_id: str
    entity_type: str
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeRelation:
    source: str
    relation: str
    target: str
    confidence: float = 1.0
    provenance: tuple[str, ...] = ()
    attributes: dict[str, Any] = field(default_factory=dict)


class KnowledgeGraph:
    """Typed, provenance-aware knowledge graph built over unified memory.

    The graph is deliberately independent from storage: callers can rebuild it
    from UnifiedMemory records without changing AIMemoryV2 persistence.
    """
    def __init__(self):
        self.entities: dict[str, KnowledgeEntity] = {}
        self.relations: list[KnowledgeRelation] = []
        self._out: dict[str, list[KnowledgeRelation]] = defaultdict(list)
        self._in: dict[str, list[KnowledgeRelation]] = defaultdict(list)
        self._keys: set[tuple[str, str, str]] = set()

    def upsert_entity(self, entity_id: str, entity_type: str = "entity", **attributes: Any) -> KnowledgeEntity:
        existing = self.entities.get(entity_id)
        merged = dict(existing.attributes) if existing else {}
        merged.update(attributes)
        entity = KnowledgeEntity(str(entity_id), str(entity_type), merged)
        self.entities[entity.entity_id] = entity
        return entity

    def relate(
        self,
        source: str,
        relation: str,
        target: str,
        *,
        confidence: float = 1.0,
        provenance: Iterable[str] = (),
        **attributes: Any,
    ) -> KnowledgeRelation:
        if source not in self.entities or target not in self.entities:
            raise KeyError("both entities must exist before creating a relation")
        confidence = max(0.0, min(1.0, float(confidence)))
        key = (source, relation, target)
        if key in self._keys:
            for edge in self.relations:
                if (edge.source, edge.relation, edge.target) == key:
                    return edge
        edge = KnowledgeRelation(source, relation, target, confidence, tuple(provenance), dict(attributes))
        self.relations.append(edge)
        self._out[source].append(edge)
        self._in[target].append(edge)
        self._keys.add(key)
        return edge

    def outgoing(self, entity_id: str, relation: str | None = None) -> list[KnowledgeRelation]:
        return [e for e in self._out.get(entity_id, ()) if relation is None or e.relation == relation]

    def incoming(self, entity_id: str, relation: str | None = None) -> list[KnowledgeRelation]:
        return [e for e in self._in.get(entity_id, ()) if relation is None or e.relation == relation]

    def traverse(self, start: str, *, relation: str | None = None, max_depth: int = 2) -> list[tuple[str, int]]:
        if start not in self.entities:
            return []
        if max_depth < 0:
            raise ValueError("max_depth must be non-negative")
        seen = {start}
        queue = deque([(start, 0)])
        result: list[tuple[str, int]] = []
        while queue:
            node, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for edge in self.outgoing(node, relation):
                if edge.target not in seen:
                    seen.add(edge.target)
                    result.append((edge.target, depth + 1))
                    queue.append((edge.target, depth + 1))
        return result

    def query_relation(self, relation: str, *, min_confidence: float = 0.0) -> list[KnowledgeRelation]:
        return [e for e in self.relations if e.relation == relation and e.confidence >= min_confidence]

    @classmethod
    def from_unified_memory(cls, unified_memory) -> "KnowledgeGraph":
        graph = cls()
        for record in unified_memory.records():
            attrs = record.attributes
            subject = attrs.get("subject")
            obj = attrs.get("object")
            if subject is None or obj is None:
                continue
            target = str(obj)
            graph.upsert_entity(str(subject), "entity")
            graph.upsert_entity(target, "entity")
            relation = str(attrs.get("predicate", "related_to"))
            provenance = record.source_refs or (record.record_id,)
            graph.relate(str(subject), relation, target, confidence=record.confidence, provenance=provenance, source_kind=record.kind)
        return graph
