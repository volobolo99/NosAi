"""PostgreSQL adapter for the provider-neutral KnowledgeStore contract.

The adapter intentionally depends only on a DB-API-like connection supplied by
callers. NosAi therefore does not hard-code psycopg or another driver into the
core package; the driver belongs in an optional deployment dependency.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol
from uuid import UUID

from .knowledge import KnowledgeKind, KnowledgeMatch, KnowledgeQuery, KnowledgeRecord


class CursorLike(Protocol):
    def execute(self, operation: str, parameters: Sequence[Any] = ()) -> Any: ...
    def fetchone(self) -> Sequence[Any] | None: ...
    def fetchall(self) -> Sequence[Sequence[Any]]: ...

    def __enter__(self) -> "CursorLike": ...
    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None: ...


class ConnectionLike(Protocol):
    def cursor(self) -> CursorLike: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...


class PostgresKnowledgeStore:
    """Durable relational KnowledgeStore using PostgreSQL.

    This first adapter deliberately uses lexical retrieval. Vector retrieval
    will be layered on top without changing the KnowledgeStore contract.
    """

    def __init__(self, connection: ConnectionLike, *, repository: str, project: str) -> None:
        if not repository.strip() or not project.strip():
            raise ValueError("repository and project are required")
        self._connection = connection
        self._repository = repository
        self._project = project

    def put(self, record: KnowledgeRecord) -> KnowledgeRecord:
        if record.repository is not None and record.repository != self._repository:
            raise ValueError("knowledge repository scope mismatch")

        sql = """
            INSERT INTO knowledge_records
                (id, repository, project, kind, status, title, content, source_run,
                 confidence, tags, metadata, created_at, updated_at)
            VALUES
                (%s, %s, %s, %s, 'candidate', %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            record.id,
            self._repository,
            self._project,
            record.kind.value,
            record.title,
            record.content,
            record.source_run_id,
            record.confidence,
            list(record.tags),
            dict(record.metadata),
            record.created_at,
            record.created_at,
        )
        try:
            with self._connection.cursor() as cursor:
                cursor.execute(sql, params)
            self._connection.commit()
        except Exception:
            self._connection.rollback()
            raise
        return record

    def search(self, query: KnowledgeQuery) -> Sequence[KnowledgeMatch]:
        conditions = ["repository = %s", "project = %s", "confidence >= %s"]
        params: list[Any] = [self._repository, self._project, query.min_confidence]

        if query.kinds:
            conditions.append("kind = ANY(%s)")
            params.append([kind.value for kind in query.kinds])
        if query.tags:
            conditions.append("tags ?| %s")
            params.append(list(query.tags))

        terms = [term.lower() for term in query.text.split() if term.strip()]
        if terms:
            conditions.append("(" + " OR ".join("lower(title || ' ' || content) LIKE %s" for _ in terms) + ")")
            params.extend(f"%{term}%" for term in terms)

        sql = f"""
            SELECT id, kind, title, content, source_run, repository, confidence,
                   tags, metadata, created_at
            FROM knowledge_records
            WHERE {' AND '.join(conditions)}
            ORDER BY updated_at DESC, id
            LIMIT %s
        """
        params.append(query.limit)

        with self._connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        matches: list[KnowledgeMatch] = []
        for row in rows:
            record = KnowledgeRecord(
                id=UUID(str(row[0])),
                kind=KnowledgeKind(row[1]),
                title=row[2],
                content=row[3],
                source_run_id=UUID(str(row[4])) if row[4] else None,
                repository=row[5],
                confidence=float(row[6]),
                tags=tuple(row[7] or ()),
                metadata=dict(row[8] or {}),
                created_at=row[9],
            )
            matches.append(KnowledgeMatch(record=record, score=record.confidence, reasons=("postgres-lexical",)))
        return matches
