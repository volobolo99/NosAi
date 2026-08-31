from app.knowledge.conflicts import detect_conflicts
from app.knowledge.source_adapters import KnowledgeCandidate, candidates_from_records


def test_candidates_keep_provenance():
    candidates = candidates_from_records(
        [{"id": "x", "kind": "skill", "fields": {"level": 10}}],
        source_id="test",
        source_ref="commit:abc",
        source_commit="abc",
    )
    assert candidates[0].source_id == "test"
    assert candidates[0].source_commit == "abc"
    assert candidates[0].verified is False


def test_conflicting_sources_are_not_silently_resolved():
    candidates = [
        KnowledgeCandidate("x", "skill", {"level": 10}, "a", "a"),
        KnowledgeCandidate("x", "skill", {"level": 20}, "b", "b"),
    ]
    conflicts = detect_conflicts(candidates)
    assert len(conflicts) == 1
    assert conflicts[0].field == "level"
    assert {source for source, _ in conflicts[0].values} == {"a", "b"}
