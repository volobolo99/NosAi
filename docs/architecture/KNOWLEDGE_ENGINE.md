# NosAi Knowledge Engine

## Decision

Use a provider-neutral `KnowledgeStore` contract first. The CI baseline is an
in-memory deterministic store. Production persistence will be PostgreSQL, with
pgvector added behind the same contract after schema/migration and retrieval
benchmarks are established.

## Memory layers

- episodic: what happened in a run
- semantic: durable facts and lessons
- procedural: repeatable problem-solving methods
- repository: code structure and historical context
- evaluation: evidence about which strategies work

## Evidence rule

Knowledge is not automatically truth. Records carry confidence, source run,
repository, tags and metadata. Promotion into durable knowledge must happen
only after verification/evaluation policy.

## Retrieval evolution

1. deterministic lexical baseline
2. PostgreSQL metadata filtering
3. pgvector exact search for benchmark/reference recall
4. HNSW approximate search when scale requires it
5. optional Qdrant adapter only if benchmarks demonstrate a material benefit

pgvector supports exact nearest-neighbor search plus HNSW and IVFFlat approximate
indexes, with filtering and iterative scans. Exact search remains the reference
for recall benchmarking.

## Isolation

Repository and project identifiers are mandatory filters at the adapter layer
for production use. A memory result must never leak context across repositories.

## Promotion

`candidate -> verified -> durable` is the intended lifecycle. Failed or
unverified observations remain evidence, not instructions.
