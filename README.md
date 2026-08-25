# NosAi

NosAi is the full-runtime fusion project currently at version **4.19.2**.

## Repository status

The repository is now source-first: the runtime lives in `app/`, tests live in `tests/`, and CI validates the source tree directly. Runtime behavior is intentionally frozen while the architecture and source quality are audited.

## Baseline

- Version: `4.19.2`
- Release: `full-runtime-fusion-hardened`
- Python: `>=3.10`
- Runtime package: `app/`
- Test suite: `tests/`
- Build/configuration source of truth: `pyproject.toml`

## Development principles

1. Preserve runtime behavior during structural work.
2. Make changes in small, reviewable commits/PRs.
3. Run the complete regression suite after structural changes.
4. Measure performance before optimizing it.
5. Do not delete historical documentation or implementation evidence without proving it is redundant.
6. Keep repository configuration single-sourced and reproducible.

## Current roadmap

1. Repository foundation and quality gates. **Complete.**
2. Source quality and architecture audit. **In progress.**
3. Consolidate proven duplication and dead weight without changing runtime behavior.
4. Establish benchmark and regression baselines.
5. Optimize measured bottlenecks.
6. Release hardening.
