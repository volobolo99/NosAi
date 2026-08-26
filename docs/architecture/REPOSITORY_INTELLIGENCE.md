# NosAi Repository Intelligence

## Goal

Give every coding agent a small, evidence-backed repository context instead of
forcing it to scan the entire repository. Retrieval must be deterministic,
auditable and replaceable.

## Contract

`RepositoryRetriever.retrieve(task, files, limit)` returns ranked
`RepositoryCandidate` records containing:

- path
- score
- reasons
- discovered symbols

The control plane owns the contract. Retrieval providers remain adapters.

## Baseline

The first implementation uses lexical/path/symbol signals and does not execute
repository code. It is dependency-light so it can run in CI and offline mode.

## Evolution path

1. deterministic lexical retrieval
2. repository graph/dependency signals
3. commit/history signals
4. hybrid lexical + embedding retrieval
5. optional pgvector/Qdrant adapter
6. benchmark every retriever against the same task corpus

## Safety

Retrieval is read-only. It must never:

- execute repository code;
- mutate the worktree;
- install packages;
- access secrets;
- decide that a patch is correct.

## Benchmark gate

A new retriever may replace the baseline only if it improves relevance on the
NosAi retrieval corpus without unacceptable latency, determinism or recall
regressions. Provider-specific benchmarks must not become runtime dependencies.
