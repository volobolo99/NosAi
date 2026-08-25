# NosAi

NosAi is the full-runtime fusion project currently at version **4.19.2**.

## Repository status

The repository is being migrated from a release ZIP into a source-first, testable layout. The runtime behavior is intentionally frozen during this infrastructure phase.

The current release archive remains available as the migration baseline:

- `NosAi_v4_19.2_FULL_RUNTIME_FUSION.zip`

The extracted project is expected to contain the `app/` runtime, `tests/`, `docs/`, and release metadata.

## Baseline

- Version: `4.19.2`
- Release: `full-runtime-fusion-hardened`
- Python: `>=3.10`
- Existing regression suite: 154 tests passing at audit time

## Development principles

1. Preserve runtime behavior during repository migration.
2. Make changes in small, reviewable commits/PRs.
3. Run the complete regression suite after structural changes.
4. Measure performance before optimizing it.
5. Do not delete historical documentation or implementation evidence without proving it is redundant.

## Planned migration

1. Repository foundation and quality gates.
2. Source-first extraction of the runtime.
3. CI and expanded regression coverage.
4. Debugging, profiling, and optimization.
5. Release hardening.
