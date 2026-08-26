# NosAi Retrieval Benchmark v1

## Decision
Use a **small, high-quality seed set first**, then expand with failed attempts as a separate negative-evidence partition.

This gives a trustworthy positive ground truth before scale introduces label noise.

## Partitions

- `gold`: verified bug/fix examples; used for primary Recall/Precision.
- `negative`: failed strategies and unrelated fixes; used for hard-negative evaluation.
- `holdout`: frozen examples never used to tune provider/model selection.

## Admission

A positive example requires evidence that the fix passed the relevant test/verification gate.
A commit message containing `fix` is only a candidate signal; it is **not sufficient proof** for promotion into `gold`.

## Leakage prevention

Query text excludes the verified solution where possible. Patch and lesson text remain in ground truth. Commit identifiers are metadata, not semantic query input.

## Metrics

Report Recall@1/5/10, Precision@K, filtered recall by repository/project, p50/p95 latency and deterministic repeatability.

## Expansion policy

Start with a small manually/automatically curated gold set. Add failed attempts as negatives. Grow the gold set only after verification evidence is available. Freeze v1 before comparing embedding providers.
