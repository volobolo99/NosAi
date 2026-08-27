# NosAi — Master Implementation Roadmap

> **Status:** canonical planning document  
> **Date:** 2026-08-27  
> **Scope:** complete NosAi architecture, including the permanent `PlayAi` + `GuardAi` cognitive model.

## 1. Mission

NosAi is an AI system for playing NosTale through a controlled perception → reasoning → decision → action loop. The target architecture separates the operational agent from an independent supervisory intelligence.

- **PlayAi** — permanent identity of the primary AI. It is the operational pilot: understands the game state, plans, decides and executes actions in pursuit of goals.
- **GuardAi** — permanent identity of the secondary AI. It is the cognitive guardian: critiques PlayAi, predicts outcomes, estimates probabilities, runs simulations, searches alternative strategies and recommends improvements.

The names are architectural identities and must remain stable. Technical terms such as `primary` and `secondary` may be used only as implementation metadata, not as replacement identities.

## 2. Target architecture

```text
NosTale Client
      ↓
Perception / Adapter
      ↓
World Model + Shared Context
      ├──────────────────────────────┐
      ↓                              ↓
   PlayAi                         GuardAi
   ├─ Goals                       ├─ Critic
   ├─ Planner                     ├─ Predictor
   ├─ Decision Engine             ├─ Simulator
   ├─ Action Manager              ├─ Risk Engine
   └─ Operational Memory          └─ Strategy Search
      │                              │
      └──────────────┬───────────────┘
                     ↓
             Arbitration / Review
                     ↓
                 Safety Gate
                     ↓
                  Executor
                     ↓
                Real Result
                     ↓
          Memory / Learning / Replay
```

### Core rule

**PlayAi answers:** “What should I do?”  
**GuardAi answers:** “Is that actually the best/safest decision, what are the likely outcomes, and can I find something better?”

GuardAi must be able to disagree with PlayAi. Agreement is an outcome, not an assumption.

## 3. Current baseline / completed foundations

The repository baseline already contains or documents the following foundations and they must be preserved while the new architecture is integrated:

1. Stable repository/release discipline and source-first Python runtime.
2. NosTale strategy/state foundations, reward metadata and provenance concepts.
3. Live-client preflight and a Windows client adapter boundary.
4. CI, quality/security/compatibility gates and Test Center foundations.
5. Local-AI routing/backend contract foundations.
6. Primary/local cooperation modes, arbitration and dual-review concepts.
7. Versioned AI message protocol with `message_id`, `correlation_id`, `context_id` and typed message kinds.
8. Controlled shared memory with source, confidence and versioning.
9. Benchmark/AutoSet direction for adapting local inference to the host computer.
10. Dashboard/control-center direction, including automatic configuration.

These are foundations, not permission to bypass the gates below.

## 4. Roadmap status model

- **DONE:** foundation exists and is accepted as baseline.
- **INTEGRATE:** foundation exists but must be connected to the new PlayAi/GuardAi architecture.
- **TODO:** implementation required.
- **GATE:** validation required before promotion.

## 5. Master phases

### Phase 0 — Governance & baseline — DONE
- Maintain stable `main` and controlled development flow.
- Preserve CI, security, quality, compatibility and Test Center gates.
- Keep source of truth in runtime/configuration/tests.

**Exit:** baseline remains reproducible and CI-green.

### Phase 1 — Permanent identities — TODO
- Introduce `PlayAi` and `GuardAi` as canonical public/internal identities.
- Define lifecycle, contracts, capabilities, events and telemetry.
- Migrate ambiguous primary/secondary naming without breaking compatibility.

**Exit:** no architectural ambiguity about ownership of decisions.

### Phase 2 — PlayAi Core — TODO
Implement:
- perception consumer;
- world-state interpretation;
- goal manager;
- planner;
- decision engine;
- action manager;
- operational/episodic memory;
- observe → decide → act → result loop.

**Exit:** PlayAi can produce a validated action proposal from a known state.

### Phase 3 — GuardAi Core — TODO
Implement independently:
- **Critic:** detects inconsistencies and weak reasoning;
- **Predictor:** estimates success/failure/death/cost/time/reward;
- **Simulator:** evaluates future scenarios;
- **Risk Engine:** selects review depth;
- **Strategy Engine:** generates and compares alternatives.

**Exit:** GuardAi can independently challenge a PlayAi proposal and return structured evidence.

### Phase 4 — Adaptive Guard Trigger — TODO
Use review levels:
- fast/no deep review for trivial actions;
- lightweight review for ordinary actions;
- simulation for difficult encounters;
- mandatory review for high-risk, high-cost, unknown or low-confidence decisions;
- escalation on disagreement.

GuardAi must not consume maximum compute on every action.

**Exit:** review depth adapts to risk, uncertainty and available compute.

### Phase 5 — PlayAi ↔ GuardAi Protocol — INTEGRATE
Existing protocol concepts must become the live orchestration contract.

Required flow:

```text
TASK → PROPOSAL → REVIEW → SIMULATION → RECOMMENDATION → DECISION → RESULT
```

Required metadata:
- `message_id`
- `correlation_id`
- `context_id`
- `decision_id`
- protocol version
- timestamp/deadline
- confidence
- evidence references
- risk level

**Exit:** every cross-agent decision is traceable end-to-end.

### Phase 6 — Shared Context & Memory — INTEGRATE
Split memory into:
- episodic memory;
- semantic knowledge;
- strategic memory;
- prediction memory;
- failure memory.

Add provenance, confidence, versioning, conflict resolution, TTL/decay where appropriate, snapshots and rollback.

**Rule:** agents propose memory changes; an authorization gate commits authoritative knowledge.

**Exit:** both agents can operate on the same authoritative context without uncontrolled mutation.

### Phase 7 — NosTale World Model — TODO
Formalize:
- player state;
- targets;
- map/location;
- skills/cooldowns;
- HP/MP;
- buffs/debuffs;
- inventory/resources;
- combat state;
- objectives;
- rewards;
- temporal context.

Every derived fact should retain confidence/provenance where feasible.

**Exit:** state is machine-readable, replayable and suitable for simulation.

### Phase 8 — Simulation Engine — TODO
Build a controlled environment supporting:
- reset/state initialization;
- deterministic/seeded transitions;
- actions and consequences;
- combat;
- movement;
- cooldowns;
- damage/defense/resistances;
- resources;
- time;
- terminal conditions;
- batch simulation.

Design the API so it can later support RL without making RL mandatory now.

**Exit:** GuardAi can run repeatable counterfactual scenarios from a captured state.

### Phase 9 — Prediction & Probability Engine — TODO
Return structured metrics:
- success probability;
- failure probability;
- death probability;
- expected reward;
- expected cost;
- expected time;
- confidence.

Record prediction vs actual outcome and calculate prediction error. Calibrate predictions over time.

**Exit:** probability outputs are measurable and continuously evaluated against reality.

### Phase 10 — Strategy Search — TODO
Progressive implementation:
1. deterministic/rule-based alternatives;
2. local/beam search;
3. Monte Carlo;
4. MCTS;
5. value/policy methods if justified;
6. self-play/RL only after simulator/reward/dataset stability.

**Exit:** GuardAi can demonstrate when an alternative strategy is statistically or empirically superior.

### Phase 11 — Learning & self-improvement — TODO
Pipeline:

```text
Experience → Evaluation → Error Analysis → Learning → Candidate Strategy → Simulation → Benchmark → Promotion
```

Never allow unvalidated automatic code mutation in the production runtime.

**Exit:** improvements are evidence-based, replayable and reversible.

### Phase 12 — Local AI runtime — INTEGRATE
- Connect the local backend/router to GuardAi and PlayAi contracts.
- Support READY/BUSY/DEGRADED/UNAVAILABLE states.
- Keep core interfaces vendor/model agnostic.
- Define resource budgets and fallback behavior.

**Exit:** local inference participates in the same governed orchestration path.

### Phase 13 — Benchmark + AutoSet — INTEGRATE
Benchmark:
- CPU;
- GPU;
- RAM/VRAM;
- storage/latency;
- inference throughput;
- simulation throughput.

AutoSet must derive:
- model/runtime selection;
- context/batch limits;
- simulation budget;
- concurrency;
- degradation policy.

Dashboard must expose automatic configuration and benchmark results.

**Exit:** NosAi adapts itself to the actual host hardware through measured data.

### Phase 14 — Perception & client integration — TODO/GATE
- Normalize observations.
- Keep adapter and decision logic separate.
- Preserve preflight.
- Require valid/consistent world state before any real action.
- Progress from observation/dry-run toward controlled execution only after all gates pass.

**Exit:** live action is impossible when state validation fails.

### Phase 15 — Dashboard / Control Center — TODO
Views:
- PlayAi status/goal/decision/confidence;
- GuardAi risk/prediction/simulation/alternatives;
- cooperation timeline;
- disagreements and consensus;
- benchmark/AutoSet;
- memory/replay;
- dry-run/read-only/live separation.

**Exit:** an operator can understand why a decision happened without inspecting source code.

### Phase 16 — Test Center + CI — TODO/GATE
Add:
- PlayAi unit tests;
- GuardAi unit tests;
- protocol contract tests;
- simulator regression tests;
- prediction calibration tests;
- conflict/fallback/timeout tests;
- memory integrity tests;
- performance budgets;
- benchmark regressions;
- integration tests for PlayAi + GuardAi.

**Exit:** all mandatory gates pass before release promotion.

### Phase 17 — Observability — TODO
Metrics:
- end-to-end latency;
- PlayAi confidence;
- GuardAi confidence;
- agreement/disagreement rate;
- simulation count/time;
- prediction error;
- reward;
- survival/failure rate;
- resource usage.

All traces should correlate via `decision_id`, `correlation_id` and `context_id`.

**Exit:** decisions can be reconstructed and replayed.

### Phase 18 — Security & safety — TODO/GATE
Enforce:
- proposal ≠ authorization ≠ execution;
- GuardAi cannot bypass Safety Gate;
- no uncontrolled runtime/code self-modification;
- secret isolation;
- least privilege for tools/adapters;
- audit trail for configuration and memory changes.

**Exit:** a model failure cannot directly bypass architectural controls.

### Phase 19 — Performance & reliability — TODO
- profile before optimizing;
- cache repeated simulations;
- batch where beneficial;
- adaptive simulation budgets;
- controlled degradation;
- timeout/recovery;
- authoritative-state persistence.

**Exit:** predictable performance on the benchmarked machine.

### Phase 20 — Offline Validation Lab — TODO
Build a scenario corpus and replay system.

Required comparisons:
- PlayAi only vs PlayAi + GuardAi;
- strategy A vs B;
- predictor calibration;
- resource cost vs decision quality;
- difficult vs ordinary scenarios.

**Exit:** measurable evidence that GuardAi improves decisions rather than merely adding latency.

### Phase 21 — Release / live pilot — GATE
Sequence:
1. develop candidate;
2. full CI;
3. security/quality/compatibility;
4. Test Center;
5. benchmark;
6. dry-run;
7. controlled live pilot;
8. observe;
9. promote to stable;
10. retain rollback path.

**Exit:** stable release only after all gates are green.

### Phase 22 — Continuous improvement — TARGET
- GuardAi mines episodes for patterns.
- Candidate strategies are generated.
- Candidates are simulated and benchmarked offline.
- Validated strategies enter strategic knowledge.
- Prediction calibration improves over time.
- Regressions trigger rollback.

## 6. External technical inspiration

Use external projects as patterns/components to evaluate, not as blind dependencies:

- **OpenSpiel:** game search, MCTS, evaluation, imperfect-information/game algorithms.
- **Gymnasium:** environment/state/action/reset/step abstractions useful for the simulation layer.
- **PettingZoo:** multi-agent environment patterns.
- **Microsoft Agent Framework:** modern orchestration/workflow ideas; evaluate selectively.
- **AutoGen:** useful historical reference for multi-agent messaging, but do not make it a foundational dependency without a current technical justification.

## 7. Dependency order

The critical dependency chain is:

```text
Identity/contracts
      ↓
PlayAi + GuardAi core
      ↓
Protocol + Shared Context
      ↓
World Model
      ↓
Simulator
      ↓
Predictor / Risk / Strategy Search
      ↓
Arbitration + Safety Gate
      ↓
Local Runtime + AutoSet
      ↓
Perception / controlled execution
      ↓
Learning / Offline Lab
      ↓
Live Pilot
```

Do not reverse this order by adding advanced RL before the simulator and evaluation system are trustworthy.

## 8. Definition of Done for the whole project

NosAi is considered mature when:

1. PlayAi can autonomously operate the game loop.
2. GuardAi independently evaluates and challenges PlayAi.
3. GuardAi can simulate meaningful alternatives before high-impact decisions.
4. Predictions are calibrated against real outcomes.
5. Shared memory is versioned, attributable and controlled.
6. Every important decision is traceable and replayable.
7. Safety Gate separates reasoning from real execution.
8. Local inference is automatically tuned to the host machine.
9. Dashboard exposes the complete cognitive loop.
10. CI/Test Center/benchmark/security gates protect releases.
11. Learning improves validated strategies without uncontrolled runtime mutation.
12. The system degrades safely when models, resources or observations are unavailable.

## 9. AI implementation contract

An AI implementing this roadmap must:

- inspect the repository before modifying architecture;
- preserve existing working functionality;
- implement the smallest coherent gate rather than unrelated rewrites;
- add tests with each architectural feature;
- document new contracts;
- never assume an external framework is required just because it was used as inspiration;
- validate changes with CI/Test Center where available;
- prefer deterministic, observable components for safety-critical decisions;
- keep PlayAi and GuardAi responsibilities explicit;
- treat this document as the master plan and update phase status after each validated gate.
