from datetime import datetime, timezone
from uuid import uuid4

from app.control_plane.knowledge import KnowledgeKind, KnowledgeQuery, new_knowledge
from app.control_plane.knowledge_postgres import PostgresKnowledgeStore


class Cursor:
    def __init__(self, rows=()):
        self.rows = list(rows)
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None

    def execute(self, operation, parameters=()):
        self.calls.append((operation, parameters))

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0] if self.rows else None


class Connection:
    def __init__(self, rows=()):
        self.cursor_obj = Cursor(rows)
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_put_is_scoped_and_committed():
    connection = Connection()
    store = PostgresKnowledgeStore(connection, repository="NosAi", project="core")
    record = new_knowledge(KnowledgeKind.SEMANTIC, "lesson", "use a sandbox", repository="NosAi")

    assert store.put(record) == record
    assert connection.commits == 1
    assert connection.rollbacks == 0
    assert connection.cursor_obj.calls
    assert "knowledge_records" in connection.cursor_obj.calls[0][0]


def test_search_enforces_repository_and_project_scope():
    now = datetime.now(timezone.utc)
    record_id = uuid4()
    connection = Connection([
        (record_id, "semantic", "lesson", "use sandbox", None, "NosAi", 0.9, ["sandbox"], {}, now),
    ])
    store = PostgresKnowledgeStore(connection, repository="NosAi", project="core")

    results = store.search(KnowledgeQuery("sandbox", min_confidence=0.5))

    assert len(results) == 1
    assert results[0].record.id == record_id
    sql, params = connection.cursor_obj.calls[0]
    assert "repository = %s" in sql
    assert "project = %s" in sql
    assert params[0:2] == ["NosAi", "core"]
