# NosAi

NosAi is the full-runtime fusion project currently at version **4.19.2**.

## Repository status

The repository is source-first: the runtime lives in `app/`, tests live in `tests/`, and CI validates the source tree directly. Runtime behavior is protected by regression tests while the architecture and source quality are audited.

## Baseline

- Version: `4.19.2`
- Release: `full-runtime-fusion-hardened`
- Python: `>=3.10`
- Runtime package: `app/`
- Test suite: `tests/`
- Build/configuration source of truth: `pyproject.toml`

## Live-client pre-flight

NosAi never guesses how to attach to the game client. A real integration must provide an explicit `ClientAdapter` implementation and configure it as `module:attribute` through `NOSAI_CLIENT_ADAPTER` or `--client-adapter`.

Before live runtime is allowed, the pre-flight performs:

1. Python and dependency checks.
2. Runtime module import checks.
3. Client connection check.
4. Normalized client-state read check.
5. Non-destructive action-validation check (no game action is executed).

A failed live check returns exit code `1` and reports a stable check ID, phase, expected value, actual value, exception type, and exception text. The live probe is deliberately non-destructive.

Example:

```text
set NOSAI_CLIENT_ADAPTER=my_adapter:adapter
nosai-preflight --require-client
```

For machine-readable diagnostics:

```text
nosai-preflight --require-client --json
```

The required adapter contract is in `app/client/adapter.py`. The repository does not ship a fake live-client adapter: until a real adapter is supplied, `--require-client` correctly blocks instead of pretending the client is connected.

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
3. Establish the strict live-client adapter and integration contract. **In progress.**
4. Consolidate proven duplication and dead weight without changing runtime behavior.
5. Establish benchmark and regression baselines.
6. Optimize measured bottlenecks.
7. Release hardening.
