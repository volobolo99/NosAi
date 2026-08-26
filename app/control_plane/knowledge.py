"""Provider-neutral Knowledge Engine primitives for NosAi."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Mapping, Protocol, Sequence
from uuid import UUID, uuid4
class KnowledgeKind(StrEnum):
    EPISODIC="episodic"; SEMANTIC="semantic"; PROCEDURAL="procedural"; REPOSITORY="repository"; EVALUATION="evaluation"
@dataclass(frozen=True, slots=True)
class KnowledgeRecord:
    id: UUID; kind: KnowledgeKind; title: str; content: str; source_run_id: UUID|None=None; repository: str|None=None; confidence: float=0.0; tags: tuple[str,...]=(); metadata: Mapping[str,str]=field(default_factory=dict); created_at: datetime=field(default_factory=lambda:datetime.now(timezone.utc))
    def __post_init__(self):
        if not self.title.strip() or not self.content.strip(): raise ValueError("knowledge title and content are required")
        if not 0.0<=self.confidence<=1.0: raise ValueError("confidence must be between 0 and 1")
        if self.created_at.tzinfo is None: raise ValueError("created_at must be timezone-aware")
@dataclass(frozen=True, slots=True)
class KnowledgeQuery:
    text:str; kinds:tuple[KnowledgeKind,...]=(); repository:str|None=None; tags:tuple[str,...]=(); min_confidence:float=0.0; limit:int=10
    def __post_init__(self):
        if not self.text.strip(): raise ValueError("query text is required")
        if not 0.0<=self.min_confidence<=1.0: raise ValueError("min_confidence must be between 0 and 1")
        if self.limit<=0: raise ValueError("limit must be positive")
@dataclass(frozen=True, slots=True)
class KnowledgeMatch: record:KnowledgeRecord; score:float; reasons:tuple[str,...]=()
class KnowledgeStore(Protocol):
    def put(self,record:KnowledgeRecord)->KnowledgeRecord: ...
    def search(self,query:KnowledgeQuery)->Sequence[KnowledgeMatch]: ...
class InMemoryKnowledgeStore:
    def __init__(self): self._records:dict[UUID,KnowledgeRecord]={}
    def put(self,record):
        if record.id in self._records: raise ValueError(f"knowledge record already exists: {record.id}")
        self._records[record.id]=record; return record
    def search(self,query):
        terms={x.lower() for x in query.text.split() if x.strip()}; matches=[]
        for r in self._records.values():
            if query.kinds and r.kind not in query.kinds: continue
            if query.repository and r.repository!=query.repository: continue
            if r.confidence<query.min_confidence: continue
            if query.tags and not ({x.lower() for x in query.tags}&{x.lower() for x in r.tags}): continue
            text=f"{r.title} {r.content} {' '.join(r.tags)}".lower(); hits=sum(t in text for t in terms)
            if hits: matches.append(KnowledgeMatch(r,min(1.0,hits/max(1,len(terms)))*r.confidence,("lexical",)))
        matches.sort(key=lambda m:(-m.score,str(m.record.id))); return matches[:query.limit]
def new_knowledge(kind,title,content,*,source_run_id=None,repository=None,confidence=0.0,tags=(),metadata=None):
    return KnowledgeRecord(uuid4(),kind,title,content,source_run_id,repository,confidence,tuple(tags),dict(metadata or {}))
