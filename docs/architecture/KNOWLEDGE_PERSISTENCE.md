# Knowledge Persistence

## Decision

Use PostgreSQL as the system of record. Keep vector search behind the existing
KnowledgeStore contract. Add pgvector only as an optional capability after the
relational schema and provenance rules are stable.

## Core tables

- `knowledge_records`: durable knowledge and lifecycle state
- `knowledge_evidence`: observations supporting or contradicting a record
- `knowledge_links`: explicit relationships between records
- `knowledge_embeddings`: optional vector representations
- `knowledge_audit`: append-only state and provenance events

## Invariants

1. Every durable record has provenance.
2. Records are scoped by repository/project.
3. Evidence is append-only; corrections create new evidence/events.
4. Embeddings never determine truth or promotion.
5. Deletion is policy-driven and auditable.
6. The database is not allowed to execute repository code.

## Vector strategy

Phase 1: relational/lexical retrieval.
Phase 2: exact vector retrieval as the recall reference.
Phase 3: HNSW approximate retrieval only after benchmark evidence.
Phase 4: hybrid lexical + vector retrieval.

The exact retriever remains the benchmark oracle for approximate retrieval.
