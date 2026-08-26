# NosAi Test Plan

**Document:** Master Test Plan  
**Project:** NosAi  
**Repository:** `volobolo99/NosAi`  
**Baseline:** main  
**Date:** 2026-08-26  
**Current project baseline:** 4.20.0 runtime / 4.21.0 package metadata  
**Status:** Active — living engineering document

## 1. Purpose

This document defines the verification strategy for NosAi: what must be tested, at which level, with which evidence, and what conditions must be satisfied before the project can be considered ready for the next integration stage.

The plan is deliberately stricter than a simple unit-test checklist. NosAi combines perception, state normalization, strategy, planning, memory/knowledge, dashboards, diagnostics, research tooling and a future live-client/action boundary. The test strategy therefore protects both software correctness and the safety boundary around the real NosTale client.

## 2. Source of truth and current baseline

The repository README identifies `app/` as the runtime source, `tests/` as the test suite and `pyproject.toml` as the build/configuration source of truth. It also states that runtime behavior is protected by regression tests and that live-client behavior is intentionally observation-only until perception is validated. The roadmap places real-client observation and visual/game-state perception before planner/reward integration and before any separately gated action transport.

The package metadata requires Python >=3.10, uses pytest/pytest-cov for testing and exposes runtime CLIs including `nosai-preflight`, `nosai-client-probe`, `nosai-diagnostics`, `nosai-dashboard` and `nosai-knowledge-import`.

## 3. Test objectives

1. Prove that every public runtime contract behaves deterministically for valid and invalid inputs.
2. Prevent regressions in perception, canonical state projection and world-model projection.
3. Verify strategy rules and reward metadata against explicitly identified source assumptions.
4. Verify that client pre-flight and the live adapter cannot accidentally execute game actions.
5. Verify integration boundaries between perception, planning, memory/knowledge, diagnostics and dashboard components.
6. Establish reproducible performance and reliability baselines before optimization.
7. Detect packaging, dependency, lint, CI and configuration regressions early.
8. Provide auditable evidence for promotion from source-only testing to real-client observation, and later to any separately gated action transport.

## 4. Scope

### 4.1 In scope

- Python package importability and CLI entry points.
- Unit and contract tests under `tests/`.
- Perception decoding and canonical player/world projections.
- Client adapter contracts, path selection and observation-only live probing.
- Brain, planning, memory-advisory and AI contracts.
- NosTale strategy/state/reward logic.
- Knowledge normalization, graph construction and importers.
- Research crawler safety boundaries.
- Dashboard API, end-to-end flows and runtime traces.
- Control-plane and integration boundaries.
- Static data validation.
- Benchmarks and hardware-sensitive performance tests.
- CI/dependency integrity and repository quality gates.
- Failure handling, diagnostics and stable error reporting.

### 4.2 Out of scope until explicitly authorized

- Autonomous game-action execution against a live account.
- Memory patching, process injection or undocumented game-client modification.
- Treating unverified gameplay mechanics as factual ground truth.
- Production claims based only on mocks or synthetic observations.

## 5. Test levels

| Level | Goal | Required evidence |
|---|---|---|
| L0 Static | Syntax, import, lint, configuration and dependency integrity | CI logs / reports |
| L1 Unit | Individual functions/classes and edge cases | Passing pytest tests |
| L2 Contract | Stable interfaces between modules | Contract/regression tests |
| L3 Integration | Real module boundaries with controlled fixtures | Integration suite |
| L4 E2E | Complete source-runtime flows including dashboard/diagnostics | E2E evidence |
| L5 Observation | Real Windows NosTale client observation without actions | Pre-flight + probe logs |
| L6 Action-gated | Future action transport validation | Separate approval and safety gate |

Promotion between levels is sequential. Passing L1-L4 does not imply that live-client behavior is safe or correct.

## 6. Test categories and acceptance criteria

### 6.1 Core runtime and contracts

**Targets:** `app/`, AI contracts, brain/planner interfaces, configuration and CLI entry points.

Tests must cover:
- valid inputs and expected outputs;
- malformed/null/boundary inputs;
- deterministic serialization where applicable;
- stable exceptions and error IDs;
- backward-compatible public contracts;
- importability from a clean environment.

**Exit criterion:** no unexpected failures and no unresolved P0/P1 contract defects.

### 6.2 Perception and world model

**Targets:** observation decoding, player-state projection and canonical world-model projection.

Tests must verify:
- decoded observations preserve the canonical schema;
- player state maps to the expected normalized representation;
- world entities, coordinates and relevant metadata remain consistent;
- missing/partial/noisy observations fail safely;
- projection changes do not silently alter downstream contracts.

**Exit criterion:** all regression fixtures pass and every schema change has an explicit test update.

### 6.3 NosTale strategy and reward model

**Targets:** `app/nostale/strategy.py` and related planner/reward consumers.

Verify the source-derived signals and modes documented by the project, including HP/MP ratios, Dignity, grade differential, elemental/resistance signals, target distance/type, Time-Space objectives, hardcore raid state, the 100% elemental-resistance threshold signal and the `-400` Dignity guard.

Every mechanic originating from external/source material must be labelled as either:
- **verified** by reproducible observations/authoritative evidence; or
- **hypothesis** pending validation.

**Exit criterion:** no unlabelled gameplay assumption reaches a release-critical decision path.

### 6.4 Client adapter and safety boundary

The real adapter is observation-only. Tests must prove that:
- configured process names are handled correctly;
- a visible client window is required;
- normalized PID/window geometry is returned correctly;
- missing client, wrong process or malformed state produces a controlled failure;
- pre-flight performs Python/dependency, import, connection, normalized-state and non-destructive action-validation checks;
- no keyboard/mouse input, injection, memory patching or game-action transport is invoked.

**Critical safety rule:** a test that could execute an unintended live game action is a failed test design, not merely a failed result.

**Exit criterion:** all observation tests pass and a negative/safety test demonstrates that the adapter cannot cross into action execution.

### 6.5 Knowledge and research

Verify normalizers, graph links, importers and bounded crawlers. Research tests must enforce configured scope, bounded traversal, safe handling of malformed sources and absence of uncontrolled external execution.

**Exit criterion:** crawler safety-boundary tests pass and imported knowledge remains traceable to its source/provenance.

### 6.6 Dashboard and observability

Verify dashboard routes, schemas, health/diagnostic views, runtime traces and E2E flows.

Tests must include:
- valid and invalid API requests;
- schema compatibility;
- deterministic diagnostic output;
- runtime trace integrity;
- startup/shutdown behavior;
- failure visibility without exposing secrets.

**Exit criterion:** unit + integration + E2E dashboard tests pass; critical diagnostics remain available when a subsystem fails.

### 6.7 CI, packaging and dependency integrity

The CI gate must validate:
- clean installation/build;
- supported Python version;
- pytest suite;
- coverage reporting where configured;
- Ruff/static checks;
- dependency integrity;
- pinned core CI actions and reproducible configuration.

**Exit criterion:** required CI checks are green with no ignored mandatory failure.

## 7. Test inventory baseline

The repository currently contains dedicated test areas for `benchmark`, `control_plane`, `integration`, `nostale_perception` and `static_data`, plus targeted tests including AI contracts, brain behavior, memory advisory, client adapter/path/probe behavior, dashboard/API/E2E/runtime trace, hardware benchmarking and knowledge importers.

This inventory is the starting point, not the final coverage target. New runtime modules must ship with corresponding tests or an explicit documented reason why a test is not applicable.

## 8. Test data strategy

Use four fixture classes:

1. **Unit fixtures:** minimal deterministic objects and synthetic observations.
2. **Regression fixtures:** previously observed inputs that reproduce a known contract or bug.
3. **Integration fixtures:** controlled multi-module scenarios with no live game side effects.
4. **Observation captures:** sanitized real-client observations, versioned and provenance-tagged where permitted.

No secret, credential, personal account data or uncontrolled live-action command may be committed as test data.

## 9. Negative and resilience testing

Every critical subsystem must include tests for:
- missing dependencies;
- unavailable client;
- malformed observation/state;
- invalid configuration;
- timeout/cancellation;
- empty collections;
- extreme numeric values;
- incompatible schema/version;
- partial subsystem failure;
- repeated/replayed observations where relevant.

The expected behavior is fail-safe, diagnosable and non-destructive.

## 10. Performance and reliability

Performance is measured before optimization. Benchmarks should establish at minimum:
- perception processing latency;
- state normalization latency;
- planner/decision latency;
- dashboard request latency;
- memory growth over long-running cycles;
- sustained cycle stability;
- startup/pre-flight duration.

Performance changes are accepted only when measured against a stored baseline and accompanied by correctness evidence.

## 11. Regression policy

For every bug fixed:

1. Reproduce the bug with a deterministic test whenever practical.
2. Implement the fix.
3. Run the focused test.
4. Run the complete regression suite.
5. Record the affected contract/component.
6. Keep the regression test permanently unless the underlying contract is intentionally removed.

Structural refactors must preserve behavior unless the change is explicitly documented as intentional.

## 12. CI gate sequence

Recommended mandatory order:

1. Repository checkout and environment setup.
2. Dependency/install integrity.
3. Static/lint checks.
4. Import/package smoke tests.
5. Unit tests.
6. Contract/regression tests.
7. Integration tests.
8. E2E/dashboard tests.
9. Benchmark smoke checks (full performance benchmarks may be scheduled separately).
10. Artifact/report publication.

A failure in an earlier safety or contract gate blocks promotion to later gates.

## 13. Severity model

| Severity | Meaning | Release rule |
|---|---|---|
| P0 | Safety breach, unintended live action, data loss or unrecoverable runtime failure | Immediate block |
| P1 | Core contract broken, perception corruption, major integration failure | Block |
| P2 | Significant feature/regression issue with workaround | Fix before relevant release |
| P3 | Minor defect, diagnostics/usability issue | Track and prioritize |
| P4 | Cosmetic/non-critical improvement | Backlog |

## 14. Release and promotion gates

### Gate A — Source quality

Required: clean install, static checks, unit suite, contract suite and reproducible CI.

### Gate B — Runtime integration

Required: integration/E2E suite, dashboard/diagnostics verification, regression suite and no P0/P1 defects.

### Gate C — Real-client observation

Required: Gate A + B, explicit client adapter configuration, pre-flight success, observation-only probe success, sanitized observation fixtures and evidence that no action path is reachable.

### Gate D — Validated perception/planning

Required: stable observation schema, canonical player/world projections, verified strategy inputs, planner/reward regression suite and benchmark baseline.

### Gate E — Future action transport

This is a separate project gate. It must not be inferred from passing the previous gates. It requires an independently reviewed transport, explicit safety controls, kill switch, dry-run mode, audit logging, constrained permissions and dedicated live validation.

## 15. Definition of Done for a testable change

A change is test-complete when:

- the intended behavior is specified;
- affected contracts are identified;
- unit/contract/integration tests are added or updated;
- negative cases are covered for critical paths;
- regression tests exist for fixed defects;
- CI passes;
- documentation is updated when behavior or interfaces change;
- source provenance is recorded for gameplay assumptions;
- no safety boundary is weakened;
- performance impact is measured when the change affects a hot path.

## 16. Current priorities

Based on the current repository roadmap and recent changes, testing priority is:

1. Complete and stabilize perception regression coverage after the canonical observation/player/world-model projection fixes.
2. Verify the strict live-client adapter and pre-flight contract using observation-only tests.
3. Connect validated state to planner/reward/evaluation tests without introducing unverified gameplay assumptions.
4. Strengthen integration/E2E coverage across dashboard, diagnostics, control plane and runtime traces.
5. Establish benchmark baselines and long-running reliability tests.
6. Only then evaluate a separately gated action transport.

## 17. Evidence and reporting

Every release candidate should retain:
- CI run identifier;
- Python/dependency environment information;
- test result summary;
- coverage report where configured;
- benchmark comparison when relevant;
- list of known failures and accepted risks;
- client-observation evidence for Gate C or later;
- provenance for source-derived strategy rules.

## 18. Final acceptance statement

NosAi is not considered "100% functional" merely because the pytest suite is green. Full project acceptance requires successful progression through the applicable gates, especially validated real-client observation, verified state/perception contracts, integration evidence and safety controls.

The project should prefer a smaller, reproducible and auditable runtime over a larger system whose behavior cannot be demonstrated. The test plan therefore treats correctness, observability, provenance and safety as release requirements rather than optional quality improvements.
