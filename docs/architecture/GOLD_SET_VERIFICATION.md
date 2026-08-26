# Gold Set Verification Gate

A Git commit is never considered a correct solution merely because its subject contains `fix`, `bug`, or `regression`.

## Admission rule

A candidate enters `gold` only when explicit verification evidence exists:

- commit identity matches;
- test/verification command is recorded;
- exit code is zero;
- status is `verified`.

A failed candidate enters the `negative` partition. Unknown candidates remain unlabelled and are excluded from primary scoring.

## Why this matters

The retrieval benchmark is intended to measure whether NosAi can retrieve a verified solution for a new code failure. Treating unverified history as truth would contaminate the benchmark and could select an embedding model that retrieves noisy or obsolete fixes.

## Recommended evidence source

CI results are preferred because they are reproducible and tied to a commit SHA. Local/manual verification may be recorded during dataset curation, but it must preserve the exact command and result.

## Benchmark freeze

Before comparing embedding providers, freeze the `gold`, `negative`, and `holdout` partitions and record the dataset version/hash. Model selection must not change the labels.
