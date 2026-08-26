from app.knowledge.record_store import write_promoted_records
from app.knowledge.source_adapters import KnowledgeCandidate


def test_promoted_records_are_sorted_and_provenance_is_retained(tmp_path):
    path = tmp_path / "knowledge.jsonl"
    records = [
        KnowledgeCandidate("b", "item", {"name": "B"}, "noscore", "repo@2", source_commit="2", verified=True),
        KnowledgeCandidate("a", "item", {"name": "A"}, "noscore", "repo@2", source_commit="2", verified=True),
    ]
    assert write_promoted_records(path, records) == 2
    lines = path.read_text(encoding="utf-8").splitlines()
    assert '"record_id": "a"' in lines[0]
    assert '"source_commit": "2"' in lines[0]
