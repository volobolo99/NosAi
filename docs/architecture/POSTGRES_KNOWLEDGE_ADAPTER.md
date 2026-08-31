# PostgreSQL Knowledge Adapter

PostgreSQL is the durable system of record. The application depends on the
`KnowledgeStore` contract, not on a concrete database driver.

## Driver boundary

The adapter accepts a DB-API-like connection. Deployment packages may choose
psycopg or another compatible PostgreSQL driver without making it a core
runtime dependency.

## Retrieval phases

1. relational lexical retrieval;
2. pgvector exact retrieval as recall oracle;
3. HNSW approximate retrieval after benchmark approval;
4. hybrid lexical + vector reranking.

## Isolation

Every query is scoped to both `repository` and `project`. A record belonging
to another repository cannot be written through this adapter.

## Transaction behavior

Writes commit atomically. On failure the adapter rolls back and propagates the
exception. Read operations do not mutate knowledge state.

## Vector rule

Embedding similarity is a retrieval signal only. It never changes lifecycle
state and never promotes candidate knowledge to verified/durable status.
