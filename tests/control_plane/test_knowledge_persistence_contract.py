from pathlib import Path


def test_knowledge_schema_contains_provenance_and_scope() -> None:
    sql = Path("migrations/001_knowledge_persistence.sql").read_text(encoding="utf-8")
    assert "source_run UUID" in sql
    assert "repository TEXT NOT NULL" in sql
    assert "project TEXT NOT NULL" in sql
    assert "knowledge_audit" in sql


def test_evidence_and_audit_are_append_only() -> None:
    sql = Path("migrations/001_knowledge_persistence.sql").read_text(encoding="utf-8")
    assert "knowledge_evidence_immutable" in sql
    assert "knowledge_audit_immutable" in sql
    assert "is append-only" in sql


def test_embeddings_are_not_authority() -> None:
    docs = Path("docs/architecture/KNOWLEDGE_PERSISTENCE.md").read_text(encoding="utf-8")
    assert "Embeddings never determine truth or promotion" in docs
