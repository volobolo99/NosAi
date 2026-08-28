# NosAi — Canonical Master Roadmap v1

Date: 2026-08-28
Repository: `volobolo99/NosAi`
Stable baseline: `main` (`4.19.2`)
Development line: `develop/nosai-next` (`4.21.0`)

## 0. Purpose

This document is the single A-to-Z engineering roadmap for NosAi after consolidating the current GitHub implementation, the existing G0-G3 work, the offline-first evolution architecture, the Simulation/Repair pipeline, and GuardAi — EYES OF PLAYAI.

It is intentionally implementation-aware: every capability is classified as **DONE/EXISTS**, **PARTIAL**, **SPECIFICATION**, **PENDING**, or **GATED**. Existing code must be reused whenever it already provides the correct boundary. Reimplementation is allowed only when a measured gap or incompatible contract is proven.

## 1. Current repository reality

- `main` is the stable baseline at `4.19.2`.
- `develop/nosai-next` is the active development line at `4.21.0`.
- `main` and `develop/nosai-next` are currently divergent; promotion must therefore be treated as a controlled integration/reconciliation operation, not a blind merge.
- PR #102 is the broad development-line integration of GuardAi/EYES OF PLAYAI and the accumulated runtime/AI work.
- PR #103 is the focused canonical EYES OF PLAYAI architecture + master-roadmap specification.
- The current `.nosai/test-center/latest.json` on the development line points to a `main` run and therefore must not be treated as certification evidence for `develop/nosai-next`.
- Real NosTale execution remains disabled by the current safety architecture; observation and sandbox boundaries are the foundation for future controlled integration.

## 2. Architecture — one system, not parallel rewrites

```text
                         NOSAI
                           |
          +----------------+----------------+
          |                                 |
       PlayAi                             GuardAi
          |                                 |
   perception/plan              critic/risk/research/strategy
          |                                 |
          +------------- Decision Fabric ---+
                           |
                    Safety / Authorization
                           |
                    Runtime Orchestrator
                           |
             +-------------+-------------+
             |                           |
        NosTale Adapter             Telemetry
             |                           |
        Observation                 Dataset / Replay
             |                           |
             +-------------+-------------+
                           |
                    World Model / Memory
                           |
          +----------------+----------------+
          |                                 |
      Local AI / Models               Evolution Lab
          |                                 |
          +----------------+----------------+
                           |
                    Knowledge Registry
                           |
                  Validated Local Capability

GuardAi external device:
PC telemetry/video → authenticated bridge → Realme X50 Pro → EYES OF PLAYAI
```

### Mandatory plane separation

1. **Gameplay/decision plane** — authoritative local runtime.
2. **Safety plane** — Decision Fabric, policy, kill switch, recovery and authorization boundaries.
3. **Observation/telemetry plane** — normalized state, events, feature extraction and recording.
4. **Evolution plane** — research, candidate generation, simulation, evaluation, anti-forgetting and promotion.
5. **Video plane** — low-latency game view for EYES OF PLAYAI; never use the database as video transport.
6. **Cloud/control plane** — optional online synchronization, remote state, knowledge/version notifications and GuardAi coordination.

## 3. Reuse-first rule

### Existing assets to reuse directly or extend

| Existing component | Current role | Reuse target |
|---|---|---|
| `app/core/contracts.py` | canonical `WorldState`, `Goal`, `Risk`, `CandidateAction`, `Decision`, `Outcome`, `Evidence` | PlayAi, GuardAi, Mission Solver, telemetry contracts |
| `app/ai/g3_3.py` | PlayAi → GuardAi → DecisionFabric boundary; fail-closed approval; execution disabled | Guardian arbitration and EYES decision metadata |
| `app/memory/*` | typed memory, provenance/confidence, local JSON persistence, context/state contracts | GuardAi knowledge, mission history, failure memory, offline capability store |
| `app/goal_planner/*` | goal/planning foundation | Mission Solver integration |
| `app/knowledge/*` | knowledge layer | Knowledge Packs and local promotion |
| `app/evolution_lab/*` | research aggregation, candidate generation, ensemble proposal | GuardAi Strategy/Research Lab |
| `app/simulation_repair/*` | research → candidate → simulation → ensemble → evidence orchestration; replay, regression, governance and Windows evidence | Failure Lab, Strategy Lab and controlled evolution |
| `nosai/ai/evaluation*.py` | deterministic evaluation and harness | Guardian Impact Score, calibration and regression |
| `nosai/ai/training.py` | offline training foundation | continual improvement after evaluation gates |
| `nosai/ai/model_registry.py` | integrity-first model lifecycle | model/strategy/knowledge promotion |
| `nosai/ai/sandbox_inference.py` | bounded inference with telemetry evidence | safe local inference |
| `nosai/data/features.py` | versioned deterministic feature extraction | Perception Frame feature payload |
| `nosai/data/live_dataset.py` | live observation dataset | GuardAi/PlayAi training and replay |
| `nosai/data/live_pipeline.py` | live data pipeline | real observation → dataset path |
| `nosai/runtime/nostale_observer.py` | read-only live observation | EYES input and World Model feed |
| `nosai/runtime/telemetry.py` | bounded sequence/session telemetry | Perception Frame sequencing and device sync |
| `nosai/runtime/adapter.py` + sandbox | provider-neutral runtime boundary | future runtime execution gate |
| `app/dashboard/*` | dashboard server, events, observability, runtime bridge and state | PC dashboard + shared control concepts for mobile UI |
| `app/autoset.py` + `app/hardware_profile.py` | hardware detection and deterministic benchmark | PC runtime tuning and future mobile capability profile |
| `.github/workflows/*` | CI, quality, security, Test Center, benchmark, Windows/runtime workflows | release gates for every new module |

**Rule:** do not create a second memory system, second telemetry system, second decision contract, second evaluation report format, or second safety gate when an existing component already covers the need.

## 4. A-to-Z functional roadmap

### A — Architecture & Contracts
**Status: PARTIAL / EXISTING FOUNDATION**

Technical names: `Core Contracts`, `Provider-Neutral Interfaces`, `DecisionFabric`, `RuntimeAdapter`, `Evidence Contract`.

Already present: typed state/goal/action/decision/outcome/evidence contracts and provider-neutral boundaries.

Remaining: freeze the cross-device `PerceptionFrame`, `GuardRequest`, `GuardDecision`, `MissionPlan`, `KnowledgePack`, `GuardianMetrics` and versioning contracts without duplicating existing contracts.

Gate: contract tests + backward compatibility.

### B — Boot, Launcher & Lifecycle
**Status: PARTIAL / EXISTING**

Technical names: `Launcher`, `Preflight`, `Session Manager`, `Watchdog`, `Safe Shutdown`, `Recovery State Machine`.

Reuse: existing launcher, preflight and runtime recovery components.

Remaining: one canonical lifecycle shared by PC runtime and GuardAi session; explicit reconnect/degraded/offline states.

### C — Client Adapter & Observation
**Status: PARTIAL / REAL OBSERVATION FOUNDATION**

Technical names: `ClientAdapter`, `WindowsNosTaleAdapter`, `NosTaleLiveObserver`, `ObservationMapper`, `WorldModel`.

Already present: configured process discovery and observation-only boundaries; live observation ingestion exists.

Remaining: stable cross-frame entity tracking, OCR/HUD mapping, minimap/world calibration and real Windows validation.

### D — Decision & Safety
**Status: EXISTING FOUNDATION / GATED FOR REAL RUNTIME**

Technical names: `PlayAi`, `GuardAi`, `DecisionFabric`, `SafetyPolicy`, `Kill Switch`, `Permission Boundary`, `Runtime State/Recovery`.

Already present: PlayAi proposals, deterministic GuardAi evaluation, fail-closed behavior and disabled execution in G3.3; later sandbox/safety layers exist in the development line.

Remaining: unify all paths so no future action can bypass Decision Fabric or Safety Gate.

### E — EYES OF PLAYAI
**Status: SPECIFICATION / IMPLEMENTATION PENDING**

Technical names: `PerceptionFrame`, `Frame Sync`, `Eyes Overlay Renderer`, `Player View`, `Engineer View`, `Event Focus`.

Goal: Realme X50 Pro shows the same game view consumed by PlayAi plus synchronized perception, reasoning, decision and GuardAi disagreement data.

Reuse: existing observation/telemetry/dashboard concepts. Do not replace them.

### F — Failure Lab
**Status: PARTIAL / STRONG REUSABLE FOUNDATION**

Technical names: `SimulationRepairEngine`, `Failure Fingerprint`, `Root-Cause Analysis`, `Candidate Generation`, `Replay Runner`, `Regression Gate`, `Evidence Seal`.

Already present: deterministic research/candidate/simulation/ensemble/evidence flow and replay/regression infrastructure.

Remaining: connect actual gameplay failures and EYES event markers into the same pipeline and promote only validated countermeasures.

### G — GuardAi Core
**Status: SPECIFICATION + SAFETY BOUNDARY EXISTS; FULL SERVICE PENDING**

Technical names: `Guardian Critic`, `Risk Engine`, `Prediction Engine`, `Strategy Engine`, `Research Engine`, `Knowledge Promoter`.

Already present: GuardAi protocol/safety concepts and G3.3 guard boundary.

Remaining: persistent independent GuardAi service on the Realme, authenticated session, local cache and controlled online research path.

### H — Hardware & AutoSet
**Status: EXISTING / EXTEND**

Technical names: `HardwareProfile`, `AutoSetProfile`, `BenchmarkRunner`, `Process-Local Runtime Tuning`.

Already present: hardware detection, benchmark and safe process-local settings.

Remaining: make AutoSet choose bounded budgets for inference, video, telemetry and Mission Solver based on measured PC and network conditions.

### I — Inference
**Status: PARTIAL / OFFLINE FOUNDATION**

Technical names: `NosAiLLM`, `llama.cpp Adapter`, `Read-Only Inference`, `Sandbox Inference`, `Model Registry`.

Already present: local provider boundary and bounded inference/model registry work.

Remaining: real hardware/model benchmark, provider routing, fallback policy and production-quality local inference profiles.

### J — Jobs / Mission Solver
**Status: SPECIFICATION / PLANNER FOUNDATION EXISTS**

Technical names: `Mission Solver`, `Mission Utility Score`, `FAST`, `SMART`, `DEEP`, `LOW-RES/DEGRADED`.

Goal: given a mission, select the fastest high-success method supported by evidence, with time/risk/cost/confidence and alternatives.

Reuse: goal planner, memory, evaluation harness and simulation repair.

### K — Knowledge
**Status: EXISTING FOUNDATION / PROMOTION EXTENSION PENDING**

Technical names: `Knowledge Pack`, `Knowledge Maturity`, `Provenance`, `Model/Strategy Registry`, `Promotion Firewall`.

Already present: provenance, registries, immutable evidence and promotion concepts.

Remaining: one unified capability registry covering model + strategy + gameplay knowledge + GuardAi research result.

### L — Learning & Local Autonomy
**Status: PARTIAL / OFFLINE FOUNDATION**

Technical names: `Offline Training`, `Continual Learning`, `Replay Stream`, `Anti-Forgetting Gate`, `Drift Detection`, `Capability Promotion`.

Already present: evaluation/training/model-registry foundations and research architecture.

Remaining: validated continual-learning loop and measurable reduction of Guardian Dependency.

### M — Memory
**Status: EXISTING / EXTEND**

Technical names: `Working Memory`, `Episodic Memory`, `Semantic Memory`, `StateStore`, `MemoryStore`, `Context Builder`, `Retrieval Router`.

Reuse existing local stores and retrieval/context code. Evaluate Qdrant only if benchmarks prove measurable benefit; do not duplicate memory abstractions.

### N — NosTale World Model
**Status: PARTIAL / BLOCK-A FOUNDATION EXISTS**

Technical names: `WorldState`, `EntityState`, `WorldModel`, `ObservationMapper`, `Tick/Revision`, `Provenance`.

Remaining: stable entity tracking, OCR/HUD, minimap calibration, combat state, objectives, resources and validated game mechanics.

### O — Observability
**Status: EXISTING / EXTEND**

Technical names: `TelemetryCollector`, `DashboardObservability`, `Correlation IDs`, `OpenTelemetry-compatible semantics`.

Reuse current telemetry and dashboard observability. Add a canonical correlation chain for PC ↔ GuardAi ↔ mission ↔ frame ↔ decision ↔ outcome.

### P — Patch & Research Intelligence
**Status: SPECIFICATION + RESEARCH FOUNDATION EXISTS**

Technical names: `Patch Detector`, `Research Pipeline`, `Source Provenance`, `Knowledge Invalidation`, `Benchmark Refresh`.

Reuse `evolution_lab` and `simulation_repair` research modules. A patch may invalidate knowledge but must not directly modify production behavior.

### Q — Quality / Test Center
**Status: EXISTING STRONG FOUNDATION / CURRENT EVIDENCE REQUIRES RE-RUN**

Technical names: `Test Center 144`, `Regression Suite`, `Security Gates`, `Quality Gates`, `CI Evidence`, `JUnit/Coverage/SBOM`.

Important: current stored latest evidence references `main`, not `develop/nosai-next`; it cannot certify the current development line.

### R — Replay / Time Travel
**Status: PARTIAL / STRONG FOUNDATION**

Technical names: `Protected Replay Store`, `Replay Runner`, `Deterministic Replay`, `Time-Travel Debugging`, `Event Marker`.

Remaining: synchronized video + PerceptionFrame + decision + GuardAi analysis replay.

### S — Strategy Lab
**Status: PARTIAL / RESEARCH FOUNDATION EXISTS**

Technical names: `Candidate Generation`, `Beam Search`, `MCTS/Monte Carlo`, `Strategy Registry`, `Benchmark`, `A/B Validation`, `Strategy Saturation`.

MCTS/learning/self-play remain conditional on simulator/reward quality. No fixed performance claims are assumed.

### T — Telemetry & Transport
**Status: PARTIAL / LOCAL FOUNDATION EXISTS**

Technical names: `PerceptionFrame`, `Sequence`, `Timestamp`, `Realtime Control/Data`, `WebRTC Video Plane`, `DataChannel`.

Database is never video transport. Control/data and video are independently degradable.

### U — User Control & Human Override
**Status: PARTIAL / DASHBOARD FOUNDATION EXISTS**

Technical names: `Human-in-the-Loop`, `Recheck`, `Pause`, `Resume`, `Waypoint`, `Mode Switch`, `Emergency Stop`.

Remaining: secure mobile controls bound to the same authorization boundary as PC.

### V — Video / Vision
**Status: OBSERVATION FOUNDATION; REMOTE STREAM PENDING**

Technical names: `Windows Capture`, `GPU Capture`, `Encoder`, `WebRTC`, `Android Decoder`, `Overlay Renderer`.

First implementation should extend the existing visual/observation path rather than rebuild game perception from scratch.

### W — Windows Runtime
**Status: SANDBOXED / REAL-HOST VALIDATION PENDING**

Technical names: `Windows Sandbox`, `Runtime Adapter`, `Evidence Collector`, `Controlled Runtime`, `Recovery`.

Real Windows evidence must be generated on the supported host. Simulation/CI evidence is never relabeled as REAL.

### X — Explainability
**Status: SPECIFICATION / PARTIAL OBSERVABILITY**

Technical names: `Decision Rationale`, `Confidence`, `Risk`, `Evidence Graph`, `Disagreement Event`, `Decision Trace`.

Goal: user can answer “what did PlayAi see, what did it consider, why did it choose this, and what did GuardAi think?”

### Y — Yield / Measured Improvement
**Status: FRAMEWORK EXISTS / BASELINES PENDING**

Technical names: `Guardian Impact Score`, `Guardian Dependency Index`, `Mission Success`, `Time Improvement`, `Error Reduction`, `Prediction Calibration`.

No invented percentages. Every improvement claim must include baseline, sample count, evaluation window, version and confidence/calibration state.

### Z — Zero-Dependency Offline Operation
**Status: LONG-TERM TARGET**

Technical names: `Offline-First Runtime`, `Local Capability Store`, `Fallback Matrix`, `Capability Promotion`, `Guardian Dependency Reduction`.

Goal: NosAi remains operational with validated local knowledge when Internet/GuardAi are unavailable. GuardAi remains useful as auditor, researcher, safety monitor and evolution lab.

## 5. GuardAi service lifecycle

```text
User starts GuardAi on Realme
        ↓
Device identity + pairing
        ↓
Authenticated session
        ↓
Capability handshake
        ↓
GuardAi connects to control/data plane
        ↓
EYES OF PLAYAI live stream starts independently
        ↓
PerceptionFrame + telemetry synchronization
        ↓
GuardAi critic / risk / mission / strategy services
        ↓
Knowledge / failure / research events
        ↓
Validated Knowledge Pack
        ↓
NosAi local promotion
        ↓
Guardian Dependency decreases
```

Cloud is coordination/synchronization, not the permanent brain.

## 6. Reusable code strategy — what must NOT be rebuilt

1. Do not rebuild core contracts.
2. Do not rebuild the existing memory layer.
3. Do not create a second simulation engine: extend `simulation_repair` where semantics match.
4. Do not create a second research engine: extend `evolution_lab`/`simulation_repair` research paths.
5. Do not create a second model registry: extend `nosai/ai/model_registry.py` into a broader capability registry only if a clean migration path exists.
6. Do not create a second Test Center/report format.
7. Do not create a second telemetry event model without a migration plan.
8. Do not bypass Decision Fabric/Safety Gate for mobile commands.
9. Do not replace the existing dashboard server/runtime bridge; reuse its API/state patterns for EYES.
10. Do not rebuild the observation-only Windows boundary to implement video; add a video plane alongside it.

## 7. Implementation sequence

### Gate A — Consolidation
- Freeze canonical contracts.
- Reconcile `main` and `develop` divergence through controlled promotion work.
- Mark every existing G3/P0/P1 feature with real CI evidence.

### Gate B — World/Perception
- Complete live observation mapping.
- Stable entity tracking.
- OCR/HUD and minimap calibration.
- PerceptionFrame v1.

### Gate C — PlayAi/GuardAi
- Integrate existing DecisionFabric.
- Build persistent GuardAi service boundary.
- Implement disagreement/recheck flow.

### Gate D — EYES OF PLAYAI
- PC capture.
- WebRTC video plane.
- Realme decoder.
- Player View.
- Engineer View.
- Event Focus.
- Frame/telemetry synchronization.

### Gate E — Mission/Strategy
- Mission Solver.
- Strategy Lab.
- Guardian Impact/Dependency metrics.

### Gate F — Failure/Evolution
- Failure Lab integration.
- Replay/time-travel.
- Candidate → simulation → regression → promotion.
- Anti-forgetting.

### Gate G — Offline Autonomy
- Knowledge Pack promotion.
- Local capability store.
- Drift detection.
- Continual-learning benchmark.
- Offline survivability test.

### Gate H — Real Windows / Controlled Live
- Windows host evidence.
- Observation-first validation.
- Controlled dry-run.
- Safety/authorization certification.
- Explicit human confirmation before any future live capability promotion.

### Gate I — Continuous Research
- Patch detection.
- Knowledge invalidation.
- Online research.
- Candidate benchmark.
- Consolidation.

## 8. Definition of Done for the whole project

NosAi is considered production-ready only when:

- stable local runtime is reproducible;
- World Model is validated against real observations;
- PlayAi decisions pass GuardAi/DecisionFabric policy;
- Mission Solver decisions are measured against baseline;
- EYES OF PLAYAI is synchronized and independently degradable;
- Failure Lab can reproduce important failures;
- Strategy Lab can validate candidates without automatic production mutation;
- Knowledge Packs have provenance and rollback references;
- anti-forgetting prevents regression of established capabilities;
- real Windows evidence exists for applicable gates;
- Test Center/CI/security are green for the candidate;
- offline operation survives loss of Internet/GuardAi;
- Guardian Dependency is demonstrably reduced by knowledge promotion.

## 9. Current completion interpretation

The repository is **not** a blank project and must not be restarted. It already contains substantial reusable foundations across contracts, memory, planning, local inference, evaluation, training, registries, simulation/repair, runtime safety, observation, telemetry, dashboard, AutoSet and CI/security.

The major missing work is integration and validation: turning those pieces into one coherent runtime, completing real Windows/observation validation, implementing the GuardAi service and EYES OF PLAYAI transport/UI, connecting Mission/Strategy/Failure systems to real gameplay evidence, and proving progressive offline autonomy.

This roadmap therefore replaces the idea of “rewrite NosAi” with **consolidate → reuse → integrate → validate → promote → learn**.
