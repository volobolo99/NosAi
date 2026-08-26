# NosAi Test Suite Audit

**Date:** 2026-08-26  
**Baseline:** `main`  
**Related:** `docs/TEST_PLAN.md` and `.github/workflows/quality.yml`

## Executive summary

The repository has a substantial test foundation: AI contracts/brain tests, client adapter and probe tests, dashboard/API/E2E/runtime-trace tests, benchmark tests, control-plane/integration suites, static-data tests and dedicated NosTale perception tests. This is **not** a greenfield testing problem.

The main risk is coverage depth and execution confidence. Several important runtime modules need explicit contract tests, the perception suite is still narrow compared with the runtime surface, and the repository contains multiple CI workflows with overlapping quality/security responsibilities.

## Existing coverage

### AI/core
- `tests/test_ai_contracts.py`
- `tests/test_brain.py`
- `tests/test_brain_memory_advisory.py`
- AI evaluation is also gated by existing CI.

Strength: contracts are versioned and the decision boundary is immutable; `ActionIntent` is tested as data rather than execution. fileciteturn32file0L2-L10

Gap: direct coverage for the complete brain pipeline, evaluation behavior, replay-buffer semantics and confidence/safety/reward propagation.

### Client boundary
- `tests/test_client_adapter.py`
- `tests/test_client_path_selector.py`
- `tests/test_client_probe_runtime.py`
- `tests/test_ci_safety_contract.py`

Strength: the observation-only boundary is represented in the suite and the adapter contract requires `check_connection`, `read_state`, `validate_action` and `close`. fileciteturn11file0L2-L2

Gap: stronger negative tests for unavailable clients, invalid process/window state, malformed adapters and execution-like interfaces.

### Dashboard/observability
- `tests/test_dashboard.py`
- `tests/test_dashboard_e2e.py`
- `tests/test_dashboard_runtime_trace.py`

Strength: API, E2E and runtime-trace layers are separately represented. fileciteturn10file0L2-L2

Gap: partial subsystem outages, secret redaction, startup/shutdown idempotence and trace ordering/correlation.

### NosTale perception
The dedicated suite currently contains:
- `tests/nostale_perception/test_game_state_and_skill_ledger.py`
- `tests/nostale_perception/test_nostale_packet_catalog.py`

Strength: canonical GameState/skill-ledger invariants and packet catalog behavior have dedicated tests. fileciteturn35file0L2-L10

Gap: observation decoding, malformed/partial observations, entity projection, coordinate normalization, temporal consistency and sanitized real-client regression captures.

### Integration/control/benchmark/static data
Dedicated `tests/benchmark`, `tests/control_plane`, `tests/integration` and `tests/static_data` areas exist. fileciteturn24file0L2-L2

Strength: concerns are separated into dedicated suites.

Gap: explicit promotion criteria for each integration suite and clear separation between fast benchmark smoke tests and scheduled performance baselines.

## Risk matrix

| Area | State | Risk | Priority |
|---|---|---:|---:|
| AI contracts | Good baseline | Medium | P1 |
| Brain | Present | Medium | P1 |
| Brain pipeline | Needs deeper coverage | High | P0 |
| Evaluation/reward | Partial/indirect | High | P1 |
| Replay buffer | Needs explicit contract tests | Medium | P1 |
| Client adapter | Good baseline | Medium | P0 |
| Client safety boundary | Present/improving | Critical | P0 |
| Perception/GameState | Dedicated but narrow | Critical | P0 |
| Packet catalog | Present | Medium | P1 |
| Dashboard/API | Present | Medium | P1 |
| Dashboard E2E | Present | Medium | P1 |
| Runtime trace | Present | Medium | P1 |
| Control plane | Dedicated suite | Medium | P1 |
| Knowledge/importers | Targeted tests | Medium | P1 |
| Benchmarks | Present | Medium | P2 |
| Static data | Dedicated suite | Low/Medium | P2 |
| CLI entry points | CI smoke validation | Medium | P1 |
| Dependency/packaging | CI gate | Medium | P1 |

## CI audit

`quality.yml` now provides L0-L4 quality/regression checks plus separate safety and benchmark gates. The repository also has CI, Security CI, CodeQL, dependency/security scanning, launcher/build, hardware benchmark, runtime profile and SonarCloud workflows. The tree confirms this workflow surface. fileciteturn33file0L2-L2

This is useful defense in depth, but ownership should remain explicit: CI for correctness/regression; quality for package/lint/coverage; Security CI for dependency/SAST/workflow hardening; CodeQL/Sonar for static analysis; hardware benchmark for scheduled performance; runtime profile for scheduled profiling.

## CI failure found

A recent CI run passed installation, dependency validation, Ruff and Python compilation, then failed specifically at `Run regression suite`; the AI evaluation step was consequently skipped. fileciteturn17file0L2-L2

The GitHub integration did not expose the underlying log blob, so the exact failing test cannot be responsibly inferred. The failed job was re-run to obtain a fresh signal instead of guessing.

## Required next additions

1. `tests/test_brain_pipeline.py` — orchestration, ordering, failure propagation and safety gating.
2. `tests/test_ai_evaluation.py` — deterministic scoring, reward evidence and invalid inputs.
3. `tests/test_replay_buffer.py` — capacity, ordering, replay determinism and malformed records.
4. Expanded perception regression fixtures — partial/noisy observations, entity projection and temporal invariants.
5. Stronger client negative tests — unreachable client, invalid state and execution-path absence.
6. Dashboard resilience tests — subsystem failure, trace integrity and secret redaction.
7. CLI contract tests — exit codes, invalid configuration and deterministic diagnostics.

## Acceptance rule

The suite is not complete based on test count alone. Promotion requires reproducibly green authoritative CI, no unresolved P0/P1 failures, deterministic perception regression fixtures, observation-only safety tests, critical CLI/dashboard coverage, performance baselines for hot paths, and separate real-client observation evidence.

## Conclusion

**Assessment: GOOD FOUNDATION / NOT YET COMPLETE.**

The optimal strategy is to harden the existing suite rather than replace it, prioritizing perception, brain orchestration, evaluation/replay semantics and client safety, while treating CI failures as evidence-driven defects.
