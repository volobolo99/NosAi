# Code and Bug Retrieval Corpus

NosAi's first semantic-retrieval benchmark targets code failures rather than generic prose.

## Sources

The future corpus may derive from repository history, test failures, issue/PR evidence,
stack traces, affected symbols, root-cause analyses, verified patches and lessons.
Only evidence available to the repository intelligence/evaluation pipeline is eligible.

## Query vs ground truth

A benchmark query contains the observed failure: error signature, stack trace, affected
files/symbols and failed tests. Ground truth contains verified root cause, patch summary
and durable lesson. These are stored separately so retrieval cannot leak the answer.

## Safety

Before indexing, text passes conservative secret redaction. Corpus generation never
executes repository code and never promotes an unverified solution into ground truth.

## Scope isolation

Every example has repository_id and project_id. Retrieval evaluation must report both
unfiltered and scope-filtered recall.

## Admission gate

Only verified fixes can become ground-truth documents. Failed attempts remain negative
or observational evidence and must not be treated as correct solutions.

## Next benchmark stages

1. deterministic corpus/unit tests
2. real NosAi bug-history extraction
3. local embedding candidates
4. OpenAI reference embedding
5. pgvector exact retrieval
6. filtered recall/latency benchmark
7. HNSW and hybrid retrieval comparison
