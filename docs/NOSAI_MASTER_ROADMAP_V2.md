# NosAi — Master Roadmap V2

Date: 2026-08-27
Branch under active work: `develop/nosai-next`
Stable branch: `main`

> Percentages below are **engineering maturity estimates**, not claims that a test has passed. A task can be structurally complete while its real-Windows or real-NosTale validation remains incomplete.

## Executive status

| Area | Status | Estimated completion | Meaning |
|---|---|---:|---|
| Repository/release structure | 🟢 | 95% | Main/develop separation and promotion policy are established |
| CI/quality foundation | 🟢 | 85% | Core gates and runtime-profile checks exist; final real-runtime validation remains |
| Test Center / evidence model | 🟢 | 80% | Structured test/evidence/report direction is established; real collector coverage remains |
| Simulation/Repair engine | 🟡 | 70% | Error fingerprinting, research/candidate flow and ensemble model exist; hardened sandbox/replay remains |
| Online research | 🟡 | 65% | GitHub/Stack Exchange research path exists; ranking, cache and broader source governance remain |
| Candidate code generation | 🟡 | 60% | Provider boundary and structured candidates exist; isolated execution/patch evaluation remains |
| Multi-candidate ensemble | 🟡 | 65% | Composite candidate concept and conflict handling exist; full patch-level validation remains |
| Dashboard | 🟡 | 65% | Runtime/Test Center/Simulation concepts exist; Evolution dashboard and complete live data remain |
| Offline-first AI architecture | 🟡 | 55% | Architecture is now defined; major runtime adapters still need implementation |
| Local inference | 🟡 | 30% | Provider abstraction is the target; llama.cpp integration and benchmark are still pending |
| RL layer | 🟡 | 45% | RL architecture/reference exists; stable adapter + training/evaluation harness remains |
| Memory/semantic retrieval | 🟡 | 40% | Memory architecture exists; Qdrant benchmark/adapter remains |
| Continual learning / anti-forgetting | 🔴 | 25% | Architecture now defined; replay, drift, protected regression and consolidation gates remain |
| Model/strategy registry | 🔴 | 20% | Required contract defined; implementation and rollback automation remain |
| Unified observability | 🟡 | 45% | Existing telemetry exists; full correlation chain and OpenTelemetry alignment remain |
| Real Windows runtime | 🔴 | 25% | Adapter/pre-flight boundary exists; real-machine execution and evidence are still required |
| Real NosTale client | 🔴 | 15% | Observation boundary exists; full state perception and real-client validation remain |
| Real action transport | 🔴 | 5% | Intentionally gated until observation is proven |
| Autonomous evolution loop | 🔴 | 20% | End-to-end architecture defined; core gates and real validation remain |

## Phase 0 — Repository and release discipline

### Completed

- `main` reserved for confirmed/stable versions.
- `develop/nosai-next` used as integration/validation branch.
- Promotion only through validation + explicit confirmation.
- Version consistency and source-first repository model documented.

**Completion: 95%**

### Remaining

- prove the full promotion workflow with a real release candidate;
- verify all branch protection/release automation in the live repository.

## Phase 1 — Test and evidence foundation

### Completed / substantially implemented

- Test Center direction.
- Structured error annotations.
- REAL / CI / SIMULATED distinction.
- Report schema and evidence model.
- Dashboard reporting direction.
- Research/simulation report lineage.

**Completion: 80%**

### Remaining

- complete collector coverage for every runtime subsystem;
- attach screenshots/traces/process/network evidence consistently;
- complete `Send Report` publication workflow;
- verify report integrity and artifact retention in CI and on real Windows.

## Phase 2 — Research → Candidate → Simulation

### Completed / substantially implemented

- error fingerprinting;
- external research provider boundary;
- GitHub research;
- Stack Exchange research;
- candidate generation model;
- structured code-generation provider boundary;
- candidate provenance;
- multi-candidate/ensemble concept;
- composite/conflict handling;
- dashboard simulation endpoint.

**Completion: 70%**

### Remaining

- hardened sandbox with explicit OS/process/network isolation;
- patch application only inside disposable workspaces;
- replay of the original failure;
- regression suite execution against every candidate;
- candidate ranking based on measured evidence rather than simple heuristics;
- research caching and rate-limit governance;
- complete dashboard visualization.

## Phase 3 — Offline-first AI core

### Architecture now confirmed

The authoritative architecture is:

`offline gameplay core + online Evolution Lab + Promotion Firewall + real-world validation + consolidation`.

**Architecture definition: 100%**

**Implementation maturity: 55%**

### Remaining

- formal `NosAiLLM` provider interface;
- local inference adapter;
- local memory/retrieval adapter;
- RL adapter;
- capability matrix and degraded/offline behavior;
- offline startup/self-test;
- local model/strategy registry.

## Phase 4 — Local inference

### Target

Primary candidate: `llama.cpp` behind `NosAiLLM`.

Optional cloud providers remain outside the gameplay dependency path.

**Completion: 30%**

### Remaining

1. define provider contract;
2. implement llama.cpp adapter;
3. benchmark CPU/GPU/memory/latency on the target Windows machine;
4. define model packaging/versioning;
5. create offline fallback tests;
6. validate no Internet is required for gameplay.

## Phase 5 — RL and strategy learning

### Target

Stable-Baselines3 behind a NosAi RL interface; SB3-Contrib only where a measurable need exists.

**Completion: 45%**

### Remaining

- environment contract;
- action/observation schema;
- reward contract;
- offline training harness;
- replay/evaluation datasets;
- policy registry;
- protected regression set;
- real-client validation.

## Phase 6 — Continual learning and anti-forgetting

### New priority after architecture review

Use Avalanche as a reference for continual-learning scenarios, replay and metrics; use River as a reference for streaming learning and drift detection. Do not allow either to bypass the NosAi promotion firewall.

**Completion: 25%**

### Required work

1. protected historical replay set;
2. new-experience stream;
3. drift detector;
4. candidate learning run;
5. old-vs-new evaluation;
6. forgetting/regression thresholds;
7. model/strategy checkpoint;
8. rollback;
9. consolidation gate;
10. repeated-cycle benchmark.

## Phase 7 — Memory and semantic knowledge

### Target

Maintain current memory as source of truth and benchmark Qdrant as an optional semantic backend.

**Completion: 40%**

### Required work

- memory taxonomy: working/episodic/semantic/strategy/protected/candidate;
- retrieval benchmark;
- persistence/recovery tests;
- local-only operation;
- memory compaction;
- provenance links;
- rollback/versioning.

## Phase 8 — Model and strategy registry

**Completion: 20%**

### Required work

Every model/policy/strategy/knowledge snapshot needs:

`id + version + parent + source_commit + run_id + replay_snapshot + environment + metrics + validation + provenance + rollback_target`.

Then implement:

- registry storage;
- promotion states;
- rollback;
- dashboard view;
- CI validation;
- real-Windows validation.

## Phase 9 — Observability

### Target

Adopt OpenTelemetry-compatible traces/metrics and one NosAi correlation chain:

`run_id -> agent_id -> scenario_id -> state_id -> tool_call_id -> model_call_id -> evidence_id -> test_result_id`.

**Completion: 45%**

### Remaining

- instrument all AI boundaries;
- correlate runtime events and test evidence;
- redact sensitive payloads by default;
- dashboard trace drill-down;
- simulation-to-real replay correlation.

## Phase 10 — Real Windows

**Completion: 25%**

### Remaining

- self-hosted Windows runner;
- environment inventory;
- process/client observation;
- API/network evidence;
- runtime resource measurements;
- screenshots and trace capture;
- non-destructive pre-flight;
- long-running stability test.

This phase cannot be declared complete from GitHub CI alone.

## Phase 11 — Real NosTale

**Completion: 15%**

### Remaining

- verified client discovery;
- visual/game-state perception;
- normalized world state;
- player state;
- target/NPC/mob observations;
- map/position observations;
- state-to-planner integration;
- repeated real-client regression scenarios.

## Phase 12 — Action transport

**Completion: 5%**

Intentionally blocked until observation is proven.

Required gates:

`observation -> state confidence -> planning validation -> safe action contract -> sandbox/replay -> controlled real-client test -> regression -> confirmation`.

## Phase 13 — Autonomous Evolution Loop

Final target:

```text
real experience
      ↓
observation
      ↓
error/opportunity detection
      ↓
online research (when available)
      ↓
candidates
      ↓
simulation/replay
      ↓
ensemble/composition
      ↓
evaluation
      ↓
anti-forgetting gate
      ↓
offline staging
      ↓
real Windows
      ↓
real NosTale
      ↓
consolidation
      ↓
new offline baseline
      ↓
new experience
```

**Current completion: 20%**

## Priority order chosen by engineering judgment

### P0 — Must happen first

1. Harden Test Center/evidence collection.
2. Harden sandbox + replay + patch evaluation.
3. Implement Promotion Firewall.
4. Build protected regression/replay set.
5. Establish model/strategy registry contract.
6. Complete real-Windows runner and evidence path.

### P1 — Then

7. Local `NosAiLLM` + llama.cpp benchmark.
8. RL adapter + offline training harness.
9. Continual-learning/drift harness.
10. Memory benchmark + Qdrant adapter.
11. OpenTelemetry correlation.
12. Evolution dashboard.

### P2 — Later

13. Optional vLLM server path.
14. Advanced explainability.
15. Experimental RL/continual-learning algorithms.
16. Further online research providers.

## Release rule

No architectural component becomes part of `main` merely because it is implemented or passes simulation.

The required promotion chain remains:

`research -> provenance/license -> isolated prototype -> unit/integration tests -> CI -> simulation -> anti-forgetting regression -> real Windows -> real NosTale -> regression -> human confirmation -> main`.
