# NosAi Knowledge Engine

The Knowledge Engine stores evidence and lessons without coupling the Control Plane to a specific database or embedding provider.

## Memory layers
- episodic: what happened in a run
- semantic: durable facts and lessons
- procedural: repeatable problem-solving methods
- repository: code structure and history
- evaluation: evidence about which strategies work

## Decision
The initial provider is deterministic in-memory storage for CI. Production persistence will use PostgreSQL, with pgvector behind the same `KnowledgeStore` contract. Qdrant remains an optional adapter, admitted only by benchmark.

## Evidence lifecycle
`candidate -> verified -> durable`.
A failed or unverified observation is evidence, not an instruction. Every durable record carries confidence and source metadata.

## Retrieval evolution
1. deterministic lexical baseline
2. PostgreSQL metadata filtering
3. exact pgvector retrieval for recall reference
4. HNSW when scale requires approximate search
5. optional Qdrant only if it materially improves measured results

Repository/project filters are mandatory in production adapters to prevent cross-project memory leakage.
