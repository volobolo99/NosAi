# NosAi Golden Benchmark Dataset

This directory contains versioned benchmark fixtures derived from normalized replay observations.

## Integrity contract

- `schema_version` identifies the fixture schema.
- `dataset_version` identifies the benchmark release.
- `source_replay` preserves provenance without embedding raw network data here.
- `fingerprint` is a SHA-256 digest of canonical fixture metadata and reconstructed state representation.
- Scenario IDs and fingerprints must be unique.
- Invalid states are retained as negative fixtures; they must not be silently repaired.

## Promotion rule

A fixture can be promoted into a golden release only after replay reconstruction, invariant validation, deterministic planner evaluation, and regression tests pass.

Raw network captures remain outside this dataset layer. Only normalized observations or approved derived fixtures should enter the benchmark dataset.
