from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable

from app.memory_v2.models import MemoryFact, Observation, Inference, StrategyExperience
from app.m3.memory_graph import MemoryGraph
from app.memory_v2.reliability import MemoryReliability

@dataclass(frozen=True)
class MemoryRecord:
    record_id: str
    kind: str
    text: str
    confidence: float
    source_refs: tuple[str, ...] = ()
    attributes: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class MemoryHit:
    record: MemoryRecord
    score: float

class UnifiedMemory:
    """Single read model over episodic, semantic, strategic and graph memory.

    AIMemoryV2 remains the durable write/compatibility API; this layer provides
    a normalized representation and context-aware retrieval without duplicating
    the underlying stores.
    """
    def __init__(self, memory_v2, graph: MemoryGraph | None = None, reliability: MemoryReliability | None = None):
        self.memory = memory_v2
        self.graph = graph or memory_v2.graph
        self.reliability = reliability or MemoryReliability()

    def records(self) -> list[MemoryRecord]:
        store = self.memory.store
        rows: list[MemoryRecord] = []
        for x in store.observations.values():
            rows.append(MemoryRecord(x.id, "episodic", f"{x.event_type} {x.payload}", x.confidence, (x.id,), {"session_id": x.session_id, "timestamp": x.timestamp}))
        for x in store.facts.values():
            rows.append(MemoryRecord(x.id, "semantic", f"{x.subject} {x.predicate} {x.object}", x.confidence, tuple(x.source_refs), {"subject": x.subject, "predicate": x.predicate, "object": x.object}))
        for x in store.inferences.values():
            rows.append(MemoryRecord(x.id, "inference", f"{x.subject} {x.predicate} {x.object}", x.confidence, tuple(x.supporting_observations), {"status": x.status, "subject": x.subject, "predicate": x.predicate, "object": x.object}))
        for i, x in enumerate(store.strategy_experiences):
            rid = f"strategy:{i}:{x.strategy_id}"
            rows.append(MemoryRecord(rid, "strategy", f"{x.goal_type} {x.strategy_id}", 1.0 if x.success else 0.5, (), {"goal_type": x.goal_type, "strategy_id": x.strategy_id, "success": x.success, "reward": x.reward, "risk": x.risk, "context": x.context}))
        return rows

    def retrieve(
        self,
        query: str = "",
        *,
        goal: str | None = None,
        entity_ids: Iterable[str] = (),
        kinds: Iterable[str] = (),
        event_types: Iterable[str] = (),
        session_id: str | None = None,
        min_confidence: float = 0.0,
        limit: int = 20,
        graph_depth: int = 1,
    ) -> list[MemoryHit]:
        """Retrieve memory using query, goal, entity and graph context.

        The scorer deliberately stays deterministic and dependency-free: lexical
        relevance is combined with confidence, explicit goal overlap, entity
        matches, graph proximity and recency.  This makes retrieval explainable
        and keeps the layer suitable for later replacement by a learned scorer.
        """
        if limit <= 0:
            return []
        if graph_depth < 0:
            raise ValueError("graph_depth must be non-negative")

        def tokens(value: str | None) -> set[str]:
            return {t for t in (value or "").lower().replace("_", " ").split() if t}

        query_tokens = tokens(query)
        goal_tokens = tokens(goal)
        entities = {str(x).lower() for x in entity_ids}
        allowed = {str(x) for x in kinds}
        allowed_events = {str(x) for x in event_types}

        # Expand explicit entities through the lightweight graph.  The expansion
        # is intentionally bounded so retrieval cost remains predictable.
        graph_entities = set(entities)
        for entity in entities:
            graph_entities.update(
                node.lower() for node, _depth in self._graph_reachable(entity, graph_depth)
            )

        hits: list[MemoryHit] = []
        for record in self.records():
            if record.confidence < min_confidence or (allowed and record.kind not in allowed):
                continue
            if session_id is not None and record.attributes.get("session_id") != session_id:
                continue
            if allowed_events and record.kind == "episodic":
                event_type = str(record.text.split(" ", 1)[0])
                if event_type not in allowed_events:
                    continue

            text = record.text.lower()
            text_tokens = tokens(record.text)
            query_overlap = len(query_tokens & text_tokens)
            goal_overlap = len(goal_tokens & text_tokens)
            entity_overlap = sum(1 for entity in graph_entities if entity and entity in text)

            # Exact phrase matches are stronger than independent token matches.
            phrase_bonus = 1.5 if query and query.lower() in text else 0.0
            lexical = float(query_overlap) + phrase_bonus
            goal_score = float(goal_overlap) * 1.25
            entity_score = float(entity_overlap) * 1.5

            subject = str(record.attributes.get("subject", ""))
            graph_bonus = 0.0
            if subject in self.graph.nodes:
                degree = len(self.graph.neighbors(subject))
                graph_bonus += min(0.75, 0.15 * degree)
                if subject.lower() in graph_entities:
                    graph_bonus += 1.0

            # Strategy context is part of retrieval context, not opaque text.
            context = record.attributes.get("context", {})
            if isinstance(context, dict) and (goal_tokens or graph_entities):
                context_text = " ".join(f"{k} {v}" for k, v in context.items()).lower()
                graph_bonus += 0.5 * len(goal_tokens & tokens(context_text))
                graph_bonus += 0.5 * sum(1 for e in graph_entities if e in context_text)

            # Stable bounded recency bonus.  It never dominates semantic matches.
            timestamp = record.attributes.get("timestamp")
            recency = 0.0
            if timestamp is not None and query_tokens:
                try:
                    age_days = max(0.0, (datetime.now(timezone.utc) - timestamp).total_seconds() / 86400.0)
                    recency = 0.25 / (1.0 + age_days)
                except (TypeError, ValueError):
                    pass

            raw = lexical + goal_score + entity_score + graph_bonus + recency
            effective_confidence = record.confidence
            if record.kind == "semantic":
                fact = self.memory.store.facts.get(record.record_id)
                if fact is not None:
                    effective_confidence = self.reliability.assess(fact).decayed_confidence
            score = raw * effective_confidence
            if score > 0 or (not query_tokens and not goal_tokens and not entities):
                hits.append(MemoryHit(record, score))

        hits.sort(key=lambda h: (h.score, h.record.confidence, h.record.record_id), reverse=True)
        return hits[:limit]

    def _graph_reachable(self, start: str, max_depth: int) -> list[tuple[str, int]]:
        if start not in self.graph.nodes or max_depth <= 0:
            return []
        seen = {start}
        frontier = [(start, 0)]
        result: list[tuple[str, int]] = []
        while frontier:
            node, depth = frontier.pop(0)
            if depth >= max_depth:
                continue
            for edge in self.graph.neighbors(node):
                if edge.target in seen:
                    continue
                seen.add(edge.target)
                result.append((edge.target, depth + 1))
                frontier.append((edge.target, depth + 1))
        return result

    def assess_fact_reliability(self, fact_id: str, *, now: datetime | None = None):
        fact = self.memory.store.facts.get(fact_id)
        if fact is None:
            raise KeyError(fact_id)
        return self.reliability.assess(fact, now=now)

    def reliable_facts(self, *, min_confidence: float = 0.0, now: datetime | None = None) -> list[MemoryFact]:
        return [
            fact for fact in self.memory.store.facts.values()
            if self.reliability.usable(fact, min_confidence=min_confidence, now=now)
        ]

    def context(self, *, query: str = "", goal: str | None = None, entity_ids: Iterable[str] = (), limit: int = 10) -> dict[str, Any]:
        hits = self.retrieve(query, goal=goal, entity_ids=entity_ids, limit=limit)
        return {"memories": [h.record for h in hits], "graph_nodes": len(self.graph.nodes), "graph_edges": len(self.graph.edges)}

    def consolidate_graph(self) -> None:
        """Idempotently mirror semantic facts into the unified graph."""
        for fact in self.memory.store.facts.values():
            self.graph.upsert_node(fact.subject, "entity")
            self.graph.upsert_node(str(fact.object), "entity")
            existing = {(e.source, e.relation, e.target) for e in self.graph.edges}
            key = (fact.subject, fact.predicate, str(fact.object))
            if key not in existing:
                self.graph.link(*key, confidence=fact.confidence)
