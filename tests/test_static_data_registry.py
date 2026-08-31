import pytest

from app.knowledge.static_data_registry import KnowledgeRecord, StaticKnowledgeRegistry


def test_registry_requires_provenance():
    registry = StaticKnowledgeRegistry()
    with pytest.raises(ValueError):
        registry.add(KnowledgeRecord("1", "item", {"name": "x"}, {}))


def test_unverified_records_are_not_queryable_as_verified():
    registry = StaticKnowledgeRegistry()
    registry.add(KnowledgeRecord("1", "item", {"name": "x"}, {"source": "test"}))
    assert registry.get_verified("item", "1") is None
    record = registry.promote_verified("item", "1")
    assert record.verified
    assert registry.get_verified("item", "1") == record
