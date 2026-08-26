"""Provider-neutral Knowledge Engine primitives for NosAi."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Mapping, Protocol, Sequence
from uuid import UUID, uuid4

class KnowledgeKind(StrEnum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    REPOSITORY = "repository"
    EVALUATION = "evaluation"

@dataclass(frozen=True, slots=True)
class KnowledgeRecord:
    id: UUID
    kind: KnowledgeKind
    title: str
    content: str
    source_run_id: UUID | None = None
    repository: str | None = None
    confidence: float = 0.0
    tags: tuple[str, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    def __post_init__(self) -> None:
        if not self.title.strip() or not self.content.strip(): raise ValueError("knowledge title and content are required")
        if not 0.0 <= self.confidence <= 1.0: raise ValueError("confidence must be between 0 and 1")
        if self.created_at.tzinfo is None: raise ValueError("created_at must be timezone-aware")

@dataclass(frozen=True, slots=True)
class KnowledgeQuery:
    text: str
    kinds: tuple[KnowledgeKind, ...] = ()
    repository: str | None = None
    tags: tuple[str, ...] = ()
    min_confidence: float = 0.0
    limit: int = 10
    def __post_init__(self) -> None:
        if not self.text.strip(): raise ValueError("query text is required")
        if not 0.0 <= self.min_confidence <= 1.0: raise ValueError("min_confidence must be between 0 and 1")
        if self.limit <= 0: raise ValueError("limit must be positive")

@dataclass(frozen=True, slots=True)
class KnowledgeMatch:
    record: KnowledgeRecord
    score: float
    reasons: tuple[str, ...] = ()

class KnowledgeStore(Protocol):
    def put(self, record: KnowledgeRecord) -> KnowledgeRecord: ...
    def search(self, query: KnowledgeQuery) -> Sequence[KnowledgeMatch]: ...

class InMemoryKnowledgeStore:
    """Deterministic baseline; production adapter can use PostgreSQL/pgvector."""
    def __init__(self) -> None: self._records: dict[UUID, KnowledgeRecord] = {}
    def put(self, record: KnowledgeRecord) -> KnowledgeRecord:
        if record.id in self._records: raise ValueError(f"knowledge record already exists: {record.id}")
        self._records[record.id] = record; return record
    def search(self, query: KnowledgeQuery) -> Sequence[KnowledgeMatch]:
        terms = {x.lower() for x in query.text.split() if x.strip()}; matches=[]
        for record in self._records.values():
            if query.kinds and record.kind not in query.kinds: continue
            if query.repository and record.repository != query.repository: continue
            if record.confidence < query.min_confidence: continue
            if query.tags and not ({x.lower() for x in query.tags} & {x.lower() for x in record.tags}): continue
            content=f"{record.title} {record.content} {' '.join(record.tags)}".lower(); hits=sum(t in content for t in terms)
            if hits: matches.append(KnowledgeMatch(record, min(1.0,hits/max(1,len(terms)))*record.confidence, ("lexical",)))
        matches.sort(key=lambda m:(-m.score,str(m.record.id))); return matches[:query.limit]

def new_knowledge(kind: KnowledgeKind, title: str, content: str, *, source_run_id: UUID | None = None, repository: str | None = None, confidence: float = 0.0, tags: Sequence[str] = (), metadata: Mapping[str, str] | None = None) -> KnowledgeRecord:
    return KnowledgeRecord(id=uuid4(), kind=kind, title=title, content=content, source_run_id=source_run_id, repository=repository, confidence=confidence, tags=tuple(tags), metadata=dict(metadata or {}))
