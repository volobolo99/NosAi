# NosAi Implementation Roadmap

## Objective

Build NosAi incrementally from a verified core to a controlled real-runtime integration. `main` remains the stable baseline; all new work lands in `develop/nosai-next` or focused feature branches and is promoted only after the release gates pass.

## Engineering order

### G0 — Repository and configuration foundation
- Keep `pyproject.toml` as the single build/version source of truth.
- Verify package discovery, entry points, configuration loading, logging and error handling.
- Remove duplicate or conflicting configuration only when equivalence is proven.
- Gate: install/build + static checks + baseline tests.

### G1 — Core runtime contract
- Stabilize lifecycle/state/event abstractions.
- Define explicit interfaces between core, AI, memory, planner, adapters and dashboard.
- Keep side effects behind interfaces.
- Gate: unit + integration tests for lifecycle, state and event flow.

### G2 — Runtime orchestration
- Stabilize launcher, scheduler, watchdog, health state and controlled shutdown/recovery.
- Add deterministic simulation mode for tests.
- Gate: repeated start/stop/recovery tests with no live-client side effects.

### G3 — AI stack
- Primary AI provider abstraction.
- Local secondary AI as a bounded fallback/support path.
- Model/router policy with timeout, confidence and failure handling.
- No provider-specific assumptions in the core.
- Gate: deterministic provider mocks, fallback tests and latency/error tests.

### G4 — Memory and planning
- Working memory and persistent intelligent memory interfaces.
- Goal planner and state/context model.
- Provenance and confidence metadata for learned/source-derived knowledge.
- Gate: persistence, recovery, context isolation and planner regression tests.

### G5 — Adapter boundary
- Keep `ClientAdapter` explicit and replaceable.
- Read-only observation adapter first.
- Dry-run action adapter second; real actions remain disabled until their validation gate is satisfied.
- Gate: adapter contract tests and non-destructive live pre-flight.

### G6 — Test Center and certification
- Consolidate unit, integration, regression and security checks into the Test Center.
- Preserve JUnit/coverage artifacts.
- Make Test Center 144 a certification gate for the affected scope.
- Gate: all applicable checks green and artifacts retained.

### G7 — CI/CD certification
- CI must validate source, tests, security, coverage and build artifacts.
- Candidate branches cannot be promoted while a release-blocking gate is red or unverified.
- Gate: complete CI on the candidate commit.

### G8 — Hardware benchmark and AutoSet
- Detect the actual Windows hardware profile.
- Benchmark CPU/RAM/GPU/runtime characteristics.
- Convert measured results into bounded profiles: safe, balanced and performance.
- Persist the selected profile and expose it to the runtime/dashboard.
- Gate: repeatable benchmark results and configuration validation.

### G9 — Dashboard/control plane
- Expose runtime health, AI providers, memory, planner, adapters, benchmark, AutoSet, Test Center, CI and diagnostics.
- Every control must report state and failures explicitly.
- Destructive/live controls remain guarded by capability and mode checks.
- Gate: dashboard API/UI integration tests.

### G10 — Real runtime integration
- Run the complete non-destructive pre-flight.
- Connect only through the configured adapter boundary.
- Start with observation/read-only mode, then validated dry-run behavior.
- Promote capabilities only after corresponding tests and diagnostics pass.
- Gate: live-client validation with no unexplained failure.

### G11 — Hardening
- Stress, timeout, recovery, concurrency, persistence and regression testing.
- Fault injection for provider, adapter, filesystem and runtime failures.
- Verify safe shutdown and recovery behavior.
- Gate: release candidate certification.

### G12 — Release
- Version metadata synchronized.
- Changelog/release notes updated.
- Full CI/Test Center green.
- No unresolved release blocker.
- Explicit confirmation required before `develop/nosai-next` is promoted to `main`.

## Standard development loop

`specification -> implementation -> unit tests -> integration tests -> Test Center -> CI -> benchmark -> optimization -> documentation -> gate`

## Rules

1. Do not optimize before measuring.
2. Do not connect new side effects directly into the core.
3. Do not replace working components without regression evidence.
4. Do not promote an unvalidated candidate.
5. Treat source-derived gameplay mechanics as hypotheses until independently validated.
6. Keep live-client work observation-first and reversible.
