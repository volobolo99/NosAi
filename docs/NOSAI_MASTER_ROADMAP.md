# NosAi — Master Implementation Roadmap v2.0

> **Status:** canonical planning document / architecture-consolidated  
> **Date:** 2026-08-28  
> **Scope:** complete NosAi architecture, including PlayAi, GuardAi, Decision Fabric, GuardAi EYES OF PLAYAI, Realme X50 Pro, Mission Solver, Failure Lab, offline autonomy and governed live execution.

## 1. Mission

NosAi is an AI system for controlled game interaction through a perception → world model → reasoning → decision → authorization → action loop.

- **PlayAi** — operational pilot: interprets state, plans, decides and executes.
- **GuardAi** — independent guardian and intelligence coprocessor: critiques, predicts, searches alternatives, researches, analyzes failures and helps train NosAi toward offline autonomy.
- **Decision Fabric** — governed coordination plane separating proposal, review, arbitration, authorization and execution.
- **EYES OF PLAYAI** — GuardAi live-observability layer on the dedicated Realme X50 Pro. It shows the game view plus PlayAi perception, reasoning, decision data and GuardAi analysis.

**Core rule:** PlayAi proposes what to do. GuardAi evaluates whether it is good, safe and improvable. Decision Fabric authorizes what may actually execute.

## 2. Target architecture

```text
                         NosTale
                            │
                            ▼
                    Capture / Adapter
                            │
                            ▼
                     World Model
                       │       │
                 ┌─────┘       └─────┐
                 ▼                   ▼
              PlayAi              GuardAi
                 │                   │
          perception/plans      critic/predictor
          decisions/actions     simulator/risk/search
                 │                   │
                 └─────────┬─────────┘
                           ▼
                    Decision Fabric
              proposal → review → arbitration
                     → authorization
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                Safety Gate   Observability
                    │             │
                    ▼             ▼
                 Executor      Replay/Memory
                    │             │
                    ▼             ▼
                 Result ─────→ Learning
                                  │
                                  ▼
                          Knowledge Promotion
                                  │
                                  ▼
                         NosAi Local Capability

PC video/telemetry: Game → GPU capture → encoder → WebRTC → Realme
Control/data: PC ↔ authenticated realtime/control transport ↔ Realme/Cloud
```

### Plane separation

1. **Video plane:** low-latency stream; never use the database as video transport.
2. **Control plane:** commands, session state, health, approvals and mode changes.
3. **Telemetry plane:** perception, decisions, metrics, events and traces.
4. **Knowledge plane:** validated strategies, failures, predictions and provenance.
5. **Safety plane:** authorization, deadlines, fallback and human override.

## 3. Review of uploaded GuardAi EYES OF PLAYAI v3.0

The v3.0 Master Architecture is a strong evolution: it turns the Realme from passive monitor into a tactical cockpit and adds synchronized telemetry, XAI, replay, formal mission scoring, disagreement analysis, hybrid storage and offline-learning concepts. It is now incorporated as architecture input, but **its performance figures are targets, not implementation facts**.

### Accepted
- Realme X50 Pro dedicated GuardAi terminal.
- EYES OF PLAYAI live view.
- Perception / Reasoning / Decision overlays.
- Frame-synchronized telemetry.
- Human-in-the-loop recheck and tactical controls.
- Replay/time-travel concept.
- Mission Utility Score.
- Failure clustering/root-cause analysis.
- DuckDB/SQLite-style local analytics.
- WebRTC + binary telemetry direction.
- OpenTelemetry-compatible observability.
- Progressive knowledge transfer to NosAi.
- Offline-first design.

### Corrections now enforced by the roadmap

**No unconditional “zero latency” or “<15 ms end-to-end” promise.** Capture, encode, network, decode, render and overlay each have separate budgets. We will publish measured p50/p95/p99 latency.

**PTS is an explicit synchronization contract.** We do not assume that a presentation timestamp is simply available in an H.264/H.265 NAL header. A monotonic media timestamp/sequence is generated and shared with telemetry.

**Protobuf is a candidate encoding, not a guaranteed payload reduction.** Any claimed reduction must come from benchmark data.

**DataChannel reliability is message-class dependent.** High-rate perception telemetry may use unordered/unreliable delivery; commands, approvals, safety events and critical state use reliable delivery.

**MCTS is adaptive.** A fixed “10,000 simulations/sec” is not a guaranteed capability. AutoSet chooses a measured simulation budget based on actual hardware and state complexity.

**TensorRT is PC-side when supported.** The Realme is not assumed to run NVIDIA TensorRT; Android handles decode/render and only assigned GuardAi workloads.

**Storage is abstracted.** DuckDB is a host analytics candidate; SQLite/Room is an Android edge-store candidate; cloud object storage is optional. No mandatory S3 dependency is assumed.

**Observability uses standard trace context.** OpenTelemetry/W3C Trace Context is the baseline; B3 may be supported only for compatibility.

**Probabilities require calibration.** Every percentage must include sample count, confidence/calibration state, evaluation window, baseline version and GuardAi version.

**Mission Utility Score is versioned, not assumed optimal.** We validate weights, normalization and scoring behavior through benchmark results.

**GuardAi cannot bypass governance.** Any correction that affects real execution passes through Decision Fabric, Safety Gate and the applicable deadline/override policy.

## 4. Status model

- **DONE** — accepted foundation exists.
- **INTEGRATE** — documented/partially present; connection required.
- **BUILD** — implementation required.
- **GATE** — validation required before promotion.
- **RESEARCH** — candidate technology/algorithm awaiting benchmark evidence.
- **TARGET** — long-term capability.

A design document is never counted as implementation.

# 5. Master phases

## Phase 0 — Governance & baseline — DONE/GATE
Preserve stable `main`, controlled PR flow, CI, security, quality, compatibility, Test Center and source-first runtime/configuration/tests.

**Exit:** reproducible baseline and green mandatory gates.

## Phase 1 — Permanent identities & contracts — INTEGRATE
Canonical identities: PlayAi, GuardAi, Decision Fabric, EYES OF PLAYAI. Define lifecycle, capabilities, health, messages, deadlines, correlation and telemetry.

**Exit:** no ambiguous ownership of decisions.

## Phase 2 — PlayAi Core — BUILD
Complete perception consumption, world interpretation, goals, planning, decision engine, action manager, operational memory and observe → decide → act → result.

**Exit:** PlayAi produces a governed proposal from validated state.

## Phase 3 — GuardAi Core — BUILD
Implement Critic, Predictor, Risk Engine, Simulator, Strategy Engine, Research Engine, Failure Lab and Knowledge Promoter. GuardAi must independently challenge PlayAi.

**Exit:** structured review with evidence.

## Phase 4 — Adaptive Guard Trigger — BUILD
Review levels: FAST, LIGHT, SMART, DEEP and SAFE/SURVIVAL. Escalate on low confidence, high risk/cost, unknown state, disagreement or repeated failure.

**Exit:** compute follows risk and uncertainty.

## Phase 5 — PlayAi ↔ GuardAi Protocol — INTEGRATE/GATE
Canonical flow:
`TASK → STATE SNAPSHOT → PROPOSAL → REVIEW → OPTIONAL SIMULATION → RECOMMENDATION → ARBITRATION → AUTHORIZATION → EXECUTION → RESULT → LEARNING EVENT`.

Every decision carries message_id, correlation_id, context_id, decision_id, protocol version, monotonic timestamp, deadline, confidence, evidence, risk and strategy version.

**Exit:** every cross-agent decision is reconstructable.

## Phase 6 — Shared Context & Memory — INTEGRATE
Logical stores: hot world state, episodic, semantic, strategic, prediction, failure, research cache and replay metadata. Authoritative knowledge requires provenance, confidence, version, promotion state and rollback.

**Exit:** no uncontrolled memory mutation.

## Phase 7 — NosTale World Model — BUILD
Formalize player, targets, map, movement, combat, skills/cooldowns, HP/MP, buffs/debuffs, inventory/resources, objectives, rewards and temporal state.

**Exit:** machine-readable, replayable, simulation-ready state.

## Phase 8 — Simulation Engine — BUILD/GATE
Build deterministic/seeded reset/state/action/transition support for movement, combat, cooldowns, resources, time and terminal states. RL is optional and comes after simulator validation.

**Exit:** repeatable counterfactual scenarios.

## Phase 9 — Prediction & Calibration — BUILD
Return success/failure/death probability where applicable, expected time/cost/reward, confidence and calibration state. Store prediction → outcome → error and evaluate calibration continuously.

**Exit:** probabilities have measurable reliability.

## Phase 10 — Mission Solver — BUILD
**FAST:** local knowledge + validated strategies.  
**SMART:** targeted research + limited simulation.  
**DEEP:** broader search/simulation.  
**LOW RES/DEGRADED:** constrained compute/network profile.

Optimize a versioned utility model balancing success, reward, time, resources, risk and retry cost.

**Exit:** plans are comparable with measured evidence.

## Phase 11 — Strategy Lab — BUILD
Lifecycle: Observed → Candidate → Sandbox → Benchmark → A/B → Stable Candidate → Approved → Knowledge Pack. Never delete the previous best automatically.

**Exit:** improvements are measurable and reversible.

## Phase 12 — Failure Lab — BUILD
Record state, perception, action sequence, decision, resources, timing, threat, disagreement and outcome. Use clustering such as DBSCAN only when data volume justifies it. Generate root cause, countermeasure, candidate strategy and replay reference.

**Exit:** failures become testable knowledge.

## Phase 13 — Learning & Offline Autonomy — TARGET
`Experience → Evaluation → Error Analysis → Candidate Learning → Simulation → Benchmark → Promotion → Local Knowledge`.

Measure Guardian Dependency Index, local decision coverage, prediction accuracy, regression rate and knowledge reuse.

**Exit:** validated autonomy grows without sacrificing safety.

## Phase 14 — GuardAi EYES OF PLAYAI Live View — BUILD
Realme X50 Pro becomes the dedicated tactical terminal. Display live game view, PlayAi perception, bounding boxes, confidence, player/target/objective, danger zones, predicted path, current/alternative strategies, decision, ETA, risk, disagreement, connection, latency and FPS.

Modes: **PLAYER VIEW** (clean) and **ENGINEER VIEW** (full diagnostic/XAI).

**Exit:** the user can see the game through PlayAi’s operational perception.

## Phase 15 — Low-Latency Video Plane — RESEARCH/BUILD
Candidate pipeline: DXGI Desktop Duplication → GPU-side processing → NVENC when available → WebRTC → Android hardware decode → overlay compositor.

DXGI Desktop Duplication is a valid frame-by-frame desktop access mechanism with GPU-oriented processing opportunities; NVENC low-latency settings will be benchmarked, not assumed.

Measure capture, encode, network, decode, render and end-to-end p50/p95/p99.

**Exit:** measured low-latency stream on the actual PC + Realme network path.

## Phase 16 — Telemetry & Frame Synchronization — BUILD/GATE
Versioned Perception Frame:
`frame_id, media_timestamp, sequence, objects[], player_state, threat, strategy_id, decision_id, top_causal_factors[]`.

Transport classes: high-rate telemetry may be lossy/unordered; commands/approvals reliable; safety events reliable + acknowledged; snapshots reliable.

**Exit:** overlay never silently applies telemetry to the wrong frame.

## Phase 17 — XAI & Human-in-the-Loop — BUILD
Show causal factors, threat, bottleneck, route, alternatives, confidence and expected result. Controls: recheck, mode switch, strategic waypoint, pause, resume and emergency stop. All controls pass through authorization.

**Exit:** the user can understand and safely influence the system.

## Phase 18 — Replay / Time-Travel Debugging — BUILD
Bounded circular buffer, initial target 30 seconds, adaptive quality and event-triggered preservation. Synchronize video, perception, reasoning, decision, candidate strategies, disagreement and outcome.

**Exit:** critical failures can be reconstructed from one timeline.

## Phase 19 — Guardian Disagreement & Safety Arbitration — BUILD/GATE
`PlayAi estimate + GuardAi estimate → confidence/risk assessment → recheck/simulation/fallback → Decision Fabric`.

Do not hard-code a universal 25% disagreement threshold. Thresholds are configurable and calibrated by scenario.

**Exit:** disagreement cannot silently become unsafe execution.

## Phase 20 — Hybrid Storage & Cloud Bridge — INTEGRATE/RESEARCH
PC: DuckDB candidate for analytical/replay workloads. Realme: SQLite/Room candidate for edge cache/offline operation. Cloud: Supabase/Postgres/Realtime for coordination and metadata where appropriate; object storage for larger artifacts when needed.

The cloud is a bridge, not the authoritative brain.

**Exit:** controlled degradation when cloud connectivity disappears.

## Phase 21 — Local AI Runtime + AutoSet — INTEGRATE
Benchmark CPU/GPU/VRAM/RAM/storage/inference/simulation/video capacity. AutoSet derives model/runtime, concurrency, context, simulation budget, GuardAi deadline, video quality and degradation policy.

**Exit:** configuration is measured, not guessed.

## Phase 22 — Observability — BUILD
Use OpenTelemetry-compatible traces, metrics and logs. Track E2E p50/p95/p99, perception FPS, overlay sync errors, PlayAi/GuardAi confidence, disagreement, prediction error, strategy win rate, mission success, resource cost, timeout/fallback, human overrides, Guardian Impact Score and Guardian Dependency Index.

**Exit:** decisions and performance are reconstructable.

## Phase 23 — Test Center & CI — GATE
Unit tests; protocol contracts; simulator regression; probability calibration; disagreement; timeout/fallback; memory integrity; replay determinism; overlay sync; WebRTC reconnect; Android offline; hardware benchmark regression; safety/override; full PlayAi + GuardAi integration.

**Exit:** no promotion without green mandatory gates.

## Phase 24 — Security, Safety & Compliance — GATE
Rules: proposal ≠ authorization ≠ execution; GuardAi cannot bypass Safety Gate; human override wins; no uncontrolled runtime/code self-modification; secrets isolated; least privilege; auditable configuration/knowledge; no anti-cheat detection-evasion mechanisms.

**Exit:** AI failure cannot directly bypass controls.

## Phase 25 — Offline Validation Lab — BUILD
Compare PlayAi only, PlayAi + GuardAi, degraded GuardAi, GuardAi-disabled fallback and strategies A/B/C. Measure success improvement, error reduction, time improvement, calibration, resource overhead and Guardian dependency.

**Exit:** GuardAi is proven useful rather than merely expensive.

## Phase 26 — Controlled Live Pilot — GATE
`Build → CI → Security → Test Center → Benchmark → Dry Run → Controlled Live → Observe → Promote`.

Rollback remains available at every promotion boundary.

**Exit:** stable pilot on actual host + Realme.

## Phase 27 — Continuous Research & Patch Intelligence — TARGET
After relevant game updates or scheduled reviews, GuardAi detects changed behavior, invalidates affected knowledge, researches new mechanics/strategies, compares evidence, benchmarks candidates, creates Knowledge Packs and requests governed promotion.

**Exit:** adaptation without destroying stable knowledge.

# 6. Dependency order

```text
Governance
 ↓
Identities & Contracts
 ↓
Decision Fabric
 ↓
PlayAi / GuardAi Core
 ↓
Protocol
 ↓
Shared Context
 ↓
World Model
 ↓
Simulator
 ↓
Prediction + Mission Solver
 ↓
Strategy Lab + Failure Lab
 ↓
Safety + Arbitration + Human Override
 ↓
Local Runtime + AutoSet
 ↓
EYES OF PLAYAI
 ↓
Live Video + Telemetry Sync
 ↓
Replay + XAI
 ↓
Offline Validation
 ↓
Controlled Live Pilot
 ↓
Continuous Research
```

Advanced RL, GPU MCTS and automatic learning must not jump ahead of simulator validity, measurement and safety gates.

# 7. Quantitative improvement framework

No improvement percentage is shown without a baseline.

For higher-is-better metrics:
`Improvement % = (with_guardai - baseline) / baseline × 100`.

For lower-is-better metrics, the direction is inverted.

Track at minimum: mission success, median/average mission time, failure rate, prediction error, resource cost, decision latency, disagreement resolution, strategy reuse and Guardian Dependency Index.

Every dashboard percentage includes sample count, calibration/confidence state, evaluation window, baseline version and GuardAi version.

# 8. Definition of Done — whole NosAi

NosAi is mature when:
1. PlayAi executes the validated game loop.
2. GuardAi independently challenges decisions.
3. Decision Fabric governs every real action.
4. Predictions are calibrated.
5. Mission Solver compares alternatives.
6. Failure Lab converts failures into validated knowledge.
7. EYES OF PLAYAI provides synchronized live observability.
8. Realme remains useful without cloud connectivity.
9. NosAi reuses validated GuardAi knowledge locally.
10. GuardAi dependency decreases over time.
11. Patch/research cycles update knowledge safely.
12. CI, Test Center, security and rollback gates remain green.

# 9. Strategic conclusion

The uploaded GuardAi v3.0 document is retained as a high-value design reference. This roadmap deliberately converts its strongest ideas into governed implementation phases and removes unsupported assumptions about latency, payload reduction, fixed MCTS throughput, timestamp placement, Android GPU capabilities and cloud storage.

The strongest architectural decision is the separation of **video, telemetry, control, knowledge and safety**, combined with a governed path from PlayAi proposal to real execution.

The Realme X50 Pro becomes the dedicated **Guardian Console + Eyes of PlayAi + XAI debugger + Mission monitor + Failure Lab terminal**.

The long-term objective remains: **GuardAi teaches NosAi until NosAi can perform validated decisions locally; GuardAi remains the independent auditor, researcher and innovation engine rather than becoming a permanent bottleneck.**
