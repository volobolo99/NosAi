from app.knowledge.import_pipeline import import_candidates
from app.knowledge.source_adapters import KnowledgeCandidate


def test_unverified_candidates_are_quarantined():
    result = import_candidates([KnowledgeCandidate("x", "item", {"name": "X"}, "web", "ref")])
    assert not result.accepted
    assert len(result.quarantined) == 1


def test_verified_non_conflicting_candidates_are_accepted():
    result = import_candidates([
        KnowledgeCandidate("x", "item", {"name": "X"}, "primary", "ref", verified=True)
    ])
    assert len(result.accepted) == 1
    assert not result.conflicts


def test_conflicting_candidates_are_quarantined():
    result = import_candidates([
        KnowledgeCandidate("x", "item", {"name": "X"}, "a", "a", verified=True),
        KnowledgeCandidate("x", "item", {"name": "Y"}, "b", "b", verified=True),
    ])
    assert not result.accepted
    assert len(result.quarantined) == 2
    assert len(result.conflicts) == 1
