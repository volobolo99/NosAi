"""SQLite-backed knowledge graph store using only the Python standard library."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .models import Edge, Evidence, KnowledgeNode, NodeType


class KnowledgeStore:
    """Transactional persistence for nodes, edges and source evidence."""

    def __init__(self, path: str | Path = "data/knowledge/nosai_knowledge.sqlite3") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _init_schema(self) -> None:
        with self._connection() as db:
            db.executescript(
                """
                PRAGMA foreign_keys = ON;
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY, type TEXT NOT NULL, title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'unknown',
                    confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 1),
                    properties_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS edges (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
                    relation TEXT NOT NULL,
                    target_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
                    confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 1),
                    properties_json TEXT NOT NULL DEFAULT '{}',
                    UNIQUE(source_id, relation, target_id)
                );
                CREATE TABLE IF NOT EXISTS evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
                    source_id TEXT NOT NULL, url TEXT, quote TEXT, observed_at TEXT, version TEXT,
                    confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 1),
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);
                CREATE INDEX IF NOT EXISTS idx_nodes_status ON nodes(status);
                CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
                CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
                CREATE INDEX IF NOT EXISTS idx_evidence_source ON evidence(source_id);
                """
            )

    def upsert_node(self, node: KnowledgeNode) -> None:
        with self._connection() as db:
            db.execute(
                """INSERT INTO nodes(id,type,title,description,status,confidence,properties_json)
                   VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET type=excluded.type,
                   title=excluded.title,description=excluded.description,status=excluded.status,
                   confidence=excluded.confidence,properties_json=excluded.properties_json""",
                (node.id, node.type.value, node.title, node.description, node.status,
                 node.confidence, json.dumps(node.properties, sort_keys=True)),
            )
            for evidence in node.evidence:
                db.execute(
                    """INSERT INTO evidence(node_id,source_id,url,quote,observed_at,version,
                       confidence,metadata_json) VALUES(?,?,?,?,?,?,?,?)""",
                    (node.id, evidence.source_id, evidence.url, evidence.quote, evidence.observed_at,
                     evidence.version, evidence.confidence, json.dumps(evidence.metadata, sort_keys=True)),
                )

    def upsert_edge(self, edge: Edge) -> None:
        with self._connection() as db:
            db.execute(
                """INSERT INTO edges(id,source_id,relation,target_id,confidence,properties_json)
                   VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET source_id=excluded.source_id,
                   relation=excluded.relation,target_id=excluded.target_id,
                   confidence=excluded.confidence,properties_json=excluded.properties_json""",
                (edge.id, edge.source_id, edge.relation, edge.target_id, edge.confidence,
                 json.dumps(edge.properties, sort_keys=True)),
            )

    def get_node(self, node_id: str) -> KnowledgeNode | None:
        with self._connection() as db:
            row = db.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
            if row is None:
                return None
            evidence_rows = db.execute("SELECT * FROM evidence WHERE node_id=? ORDER BY id", (node_id,)).fetchall()
        evidence = [Evidence(source_id=r["source_id"], url=r["url"], quote=r["quote"],
                             observed_at=r["observed_at"], version=r["version"], confidence=r["confidence"],
                             metadata=json.loads(r["metadata_json"])) for r in evidence_rows]
        return KnowledgeNode(id=row["id"], type=NodeType(row["type"]), title=row["title"],
                             description=row["description"], status=row["status"], confidence=row["confidence"],
                             properties=json.loads(row["properties_json"]), evidence=evidence)

    def neighbors(self, node_id: str, relation: str | None = None) -> list[tuple[Edge, KnowledgeNode]]:
        query = """SELECT e.id AS edge_id, e.source_id, e.relation, e.target_id,
                   e.confidence AS edge_confidence, e.properties_json AS edge_properties_json,
                   n.type AS node_type, n.title AS node_title, n.description AS node_description,
                   n.status AS node_status, n.confidence AS node_confidence,
                   n.properties_json AS node_properties_json
                   FROM edges e JOIN nodes n ON n.id=e.target_id WHERE e.source_id=?"""
        params: list[object] = [node_id]
        if relation:
            query += " AND e.relation=?"
            params.append(relation)
        query += " ORDER BY e.confidence DESC"
        with self._connection() as db:
            rows = db.execute(query, params).fetchall()
        return [
            (Edge(r["edge_id"], r["source_id"], r["relation"], r["target_id"],
                  r["edge_confidence"], json.loads(r["edge_properties_json"])),
             KnowledgeNode(r["target_id"], NodeType(r["node_type"]), r["node_title"],
                           r["node_description"], r["node_status"], r["node_confidence"],
                           json.loads(r["node_properties_json"])))
            for r in rows
        ]

    def search(self, text: str, node_type: NodeType | None = None, limit: int = 50) -> list[KnowledgeNode]:
        if limit < 1:
            return []
        pattern = f"%{text}%"
        query = "SELECT * FROM nodes WHERE (id LIKE ? OR title LIKE ? OR description LIKE ?)"
        params: list[object] = [pattern, pattern, pattern]
        if node_type:
            query += " AND type=?"
            params.append(node_type.value)
        query += " ORDER BY confidence DESC, title LIMIT ?"
        params.append(limit)
        with self._connection() as db:
            rows = db.execute(query, params).fetchall()
        return [KnowledgeNode(r["id"], NodeType(r["type"]), r["title"], r["description"],
                              r["status"], r["confidence"], json.loads(r["properties_json"])) for r in rows]

    def export_json(self) -> dict[str, object]:
        with self._connection() as db:
            nodes = db.execute("SELECT * FROM nodes ORDER BY id").fetchall()
            edges = db.execute("SELECT * FROM edges ORDER BY id").fetchall()
        return {
            "schema_version": 1,
            "nodes": [{"id": r["id"], "type": r["type"], "title": r["title"],
                        "description": r["description"], "status": r["status"],
                        "confidence": r["confidence"], "properties": json.loads(r["properties_json"])} for r in nodes],
            "edges": [{"id": r["id"], "source_id": r["source_id"], "relation": r["relation"],
                       "target_id": r["target_id"], "confidence": r["confidence"],
                       "properties": json.loads(r["properties_json"])} for r in edges],
        }

    def import_json(self, payload: dict[str, object]) -> None:
        if payload.get("schema_version") != 1:
            raise ValueError("unsupported knowledge graph schema version")
        for raw in payload.get("nodes", []):
            if not isinstance(raw, dict):
                raise ValueError("node entry must be an object")
            self.upsert_node(KnowledgeNode(id=str(raw["id"]), type=NodeType(str(raw["type"])),
                                           title=str(raw["title"]), description=str(raw.get("description", "")),
                                           status=str(raw.get("status", "unknown")),
                                           confidence=float(raw.get("confidence", 0)),
                                           properties=dict(raw.get("properties", {}))))
        for raw in payload.get("edges", []):
            if not isinstance(raw, dict):
                raise ValueError("edge entry must be an object")
            self.upsert_edge(Edge(id=str(raw["id"]), source_id=str(raw["source_id"]),
                                  relation=str(raw["relation"]), target_id=str(raw["target_id"]),
                                  confidence=float(raw.get("confidence", 1)),
                                  properties=dict(raw.get("properties", {}))))
