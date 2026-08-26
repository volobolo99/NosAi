# NosAi Memory Retrieval Benchmark

## Decision

Use exact vector similarity as the reference implementation before enabling
approximate pgvector indexes. pgvector documents that exact search provides
perfect recall while HNSW/IVFFlat trade recall for speed. The benchmark must
therefore compare every approximate strategy against exact results.

## Baseline

CI uses a deterministic hashing embedding provider. It is a test oracle for
pipeline behavior only, not a semantic-quality claim.

## Metrics

- Recall@K
- Precision@K
- deterministic ordering
- repository/project filtered recall
- query latency (integration benchmark)
- storage size (integration benchmark)

## Promotion gate

A vector index may become the default only if it preserves an agreed recall
threshold against exact retrieval and provides a meaningful latency/resource
benefit. Filtered queries are mandatory because NosAi knowledge is scoped by
repository and project.

## Planned phases

1. deterministic embedding + metrics in CI
2. real embedding provider behind the same contract
3. pgvector exact retrieval
4. benchmark corpus and filtered retrieval
5. HNSW benchmark with multiple `ef_search` values
6. hybrid lexical + vector retrieval
7. optional Qdrant comparison using the same corpus and metrics

Approximate retrieval never decides knowledge truth or promotion.
