from uuid import uuid4
import pytest
from app.control_plane.knowledge import InMemoryKnowledgeStore, KnowledgeKind, KnowledgeQuery, new_knowledge

def test_knowledge_round_trip_and_filtering() -> None:
    store=InMemoryKnowledgeStore(); rid=uuid4()
    store.put(new_knowledge(KnowledgeKind.SEMANTIC,"None guard","Check optional value before dereference",source_run_id=rid,repository="NosAi",confidence=.9,tags=["python","bugfix"]))
    store.put(new_knowledge(KnowledgeKind.EPISODIC,"Unrelated","Database migration result",repository="Other",confidence=.8))
    results=store.search(KnowledgeQuery("optional dereference",repository="NosAi",min_confidence=.5))
    assert len(results)==1 and results[0].record.kind is KnowledgeKind.SEMANTIC

def test_invalid_knowledge_is_rejected() -> None:
    with pytest.raises(ValueError): new_knowledge(KnowledgeKind.SEMANTIC,"","content")
    with pytest.raises(ValueError): new_knowledge(KnowledgeKind.SEMANTIC,"title","content",confidence=1.1)

def test_query_requires_positive_limit() -> None:
    with pytest.raises(ValueError): KnowledgeQuery("test",limit=0)
