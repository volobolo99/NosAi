# NosAi — Project Architecture Map

## 1. Mission
NosAi is an AI system focused on playing NosTale through a cooperative architecture in which **PlayAi** is the primary agent and **GuardAi** is the independent supervisory intelligence. The project prioritizes reliability, measurable decisions, simulation, safety, testability and progressive runtime integration.

## 2. High-level architecture
```text
Observation / NosTale Adapter
          |
          v
World State -> CharacterSnapshot -> Temporal World Model
          |
          v
        PlayAi
          |
   candidate plans
          v
PlayAiGuardAiBridge
          |
        GuardAi
   +------+------+------+------+
   |      |      |      |      |
Simulator Prediction Risk Trigger Adversarial Review
   |      |      |      |      |
   +------+------+------+------+
          |
          v
Decision Fabric 2.0
          |
     Decision Gate
          |
Execution Safety Monitor
          |
Execution Policy / Executor
          |
        outcome
          |
    Memory + Replay
          |
Benchmark / Evaluation / Learning
          |
Test Center + CI Quality Gates
```

## 3. Core identity
### PlayAi
Primary intelligence. Interprets the current state, manages objectives, plans strategies, selects tactical approaches and produces action intents. It remains the main decision-making agent.

### GuardAi
Secondary supervisory intelligence. Reviews PlayAi proposals, performs simulations and probability estimates, evaluates risk, searches for alternatives and can respond with **APPROVE / MODIFY / REJECT / REQUEST_MORE_SIMULATION**. Deep intervention is triggered when risk, uncertainty, novelty, confidence gaps or prior failures justify the compute cost.

### PlayAi ↔ GuardAi cooperation contract
GuardAi is not merely a scalar score attached to PlayAi. It is an independent reviewer whose structured verdict becomes evidence for the Decision Fabric. PlayAi remains the owner of the primary plan; GuardAi owns verification, challenge and alternative analysis.

## 4. Perception and state
### World State
Read-only representation of the observed game/runtime state.

### CharacterSnapshot
Normalized structured state of the character and relevant environment, carrying observed facts plus confidence/provenance.

### Temporal World Model
Time-aware belief state built from recent observations, changes, trends and anomalies.

### NosTale Adapter
Game-specific boundary under `app/adapters/`. It translates runtime observations into the generic core contract. The observation-first boundary is retained for controlled development.

### Generic Core / Adapter boundary
`app/core/adapter.py` defines the game-agnostic adapter contract and `WorldObservation`. This is intentionally small so future generalization does not slow NosAi.

## 5. Reasoning and planning
### Goal Manager / Strategy / Planner
Transforms long-term objectives into mid-term plans, current objectives and tactical decisions.

### Action Intent
Describes what PlayAi intends to accomplish before a concrete execution mechanism is selected.

### Progression Advisor / Bottleneck Detector
Evaluate progression, time, cost and risk and identify root causes limiting progress.

## 6. GuardAi intelligence
### Simulation Engine
Runs candidate strategies against a model of the state.

### Digital-Twin-style Simulator
Planned evolution covering combat, movement, resources, cooldowns, status effects, objectives and uncertainty.

### Prediction Engine + Calibration
Produces forecasts and continuously compares predictions with real outcomes to measure error and calibration.

### Risk Engine + Trigger Engine
Risk is decomposed into failure, resource, time, unknown-state and execution dimensions. Triggering determines when deeper GuardAi analysis is worth its computational cost.

### Adversarial Review
GuardAi actively attempts to disprove or improve PlayAi's plan.

## 7. Decision Fabric 2.0 — v3 specification
The baseline multi-evidence utility model for candidate action `a` is:

`U(a) = wp*C_PlayAi(a) + ws*C_Sim(a) - wr*R(a) - wl*L(a)`

This is a baseline, **not a permanently fixed policy**. Mature NosAi uses context-dependent dynamic weights. The context can increase the relative importance of simulation, risk, decision quality or latency according to the current state and compute budget.

Risk baseline:
`R(a) = alpha*R_loss(a) + beta*R_time(a) + gamma*R_uncertainty(a) + delta*R_exec(a)`

Latency must use a **bounded penalty** compatible with a hard timeout. Once the evaluation budget expires, timeout becomes a deterministic Decision Gate condition rather than an unbounded numerical penalty.

The Decision Gate authorizes execution only when acceptance threshold, maximum risk, valid state and evaluation budget constraints are satisfied. Otherwise a deterministic safe fallback is selected.

### Decision semantics
Decision Fabric consumes:
- PlayAi proposal and confidence;
- GuardAi verdict and evidence;
- simulation/prediction outputs;
- World State confidence/provenance;
- memory evidence and reliability;
- risk;
- latency and compute budget.

Its output should contain decision, confidence, risk, evidence, reason, deadline and fallback.

## 8. Operational Decision Fabric ≠ RL Reward
The operational Decision Fabric and reinforcement-learning reward function are deliberately separate. A Gymnasium environment may derive reward terms from Decision Fabric evidence, but reward must not become a rigid copy of the operational utility function. This prevents training from overfitting to an internal scoring formula.

Example reward terms can include environment/progression reward, risk penalty, stale-data penalty, time-budget penalty, survival and efficiency. The exact reward is an experimental artifact subject to benchmark validation.

## 9. Memory and learning
Intelligent Memory, Memory Reliability Layer, Counterfactual Memory and Improvement Candidates provide evidence-backed experience. Proposed changes must pass simulation, regression, benchmarks and promotion gates.

Decision Replay makes important decisions reproducible from Decision ID, state, proposals, evidence, memory references, simulation seed, Decision Fabric result and outcome.

## 10. Test Center & Decision Quality Benchmark
Test Center covers unit/contract, integration, E2E fixtures, regression, fault injection, simulation validation, performance, decision quality and safety boundaries.

Decision Quality Benchmark compares **PlayAi-only** against **PlayAi+GuardAi** on identical scenarios. Metrics include success, survival, reward, time, resource efficiency, prediction calibration, decision reversals and unnecessary GuardAi interventions.

Any number such as `<2 ms` or `60 Hz` is a **target until measured** on the actual target configuration. Documentation must never present an unverified target as an achieved result.

## 11. Reusable AI/RL research layer
External projects are research inputs and optional tooling, never wholesale replacements for NosAi Core.

Priority candidates:
- **Gymnasium** — standard RL environment API and future controlled NosTale training environment.
- **PettingZoo** — multi-agent environment patterns for formal PlayAi/GuardAi cooperation.
- **Stable-Baselines3** — optional PyTorch RL baselines for controlled experiments; never a hard runtime dependency.
- **CleanRL** — transparent reference implementations for algorithmic experiments.
- **RL Baselines3 Zoo** — reproducible RL configurations and benchmarking reference.
- **Agent Lightning** — research inspiration for trajectory-level traces/rewards and decoupled training.
- **Game-agent projects** — perception→state→policy→action→reward reference patterns.
- **MALib** — future multi-agent/distributed-learning candidate if justified by evaluation workload.

Every external component must pass the Third-Party AI Research Gate: license, maintenance, API compatibility, Python/PyTorch compatibility, security, size/overhead, reproducibility and architectural fit. Prefer small optional integrations over framework replacement.

## 12. Compute architecture
Local CPU/GPU/RAM, External SSD, Compute Broker and cloud tiers remain part of the infrastructure roadmap. Training workloads may use optional acceleration; the local runtime should remain functional without external providers.

External SSD is storage/portability, not additional compute. Cloud selection must consider latency, capacity, privacy and cost, with dashboard estimates based on measured workload data.

## 13. Dashboard
The operational cockpit exposes PlayAi objective/plan/confidence, GuardAi risk/prediction/simulation/verdict, Decision Fabric rationale, World State, memory evidence, hardware and local/cloud usage, Test Center, AutoConfig and gate status. Add an AI Research/Evaluation view for benchmark comparisons and provenance.

## 14. Execution architecture
Reasoning remains isolated from execution:
`Action Intent → Execution Policy → Execution Safety Monitor → Input Adapter → Executor/Runtime`.

The execution boundary enforces authorization, state validity, rate/timeout controls, emergency stop, audit/replay and error handling. No cognitive component may bypass the Decision Gate or Safety/Control Plane.

## 15. CI and promotion
CI is a hard evidence gate: dependency integrity, static checks, imports, tests, security checks and relevant Test Center suites. External-model evaluations are informative and must not silently become PASS when unavailable.

Development cycle:
`ANALYZE → DESIGN → IMPLEMENT → TEST → INTEGRATE → VERIFY → BENCHMARK → CORRECT → RE-VERIFY → PROMOTE`.

## 16. Architecture Hardening v3 — priority order
1. **Dynamic Decision Fabric 2.0** — context-aware weights and explicit multi-evidence decision model.
2. **GuardAi Trigger + Risk Engine** — proportional supervision.
3. **Temporal World Model** — temporal belief/state continuity.
4. **Prediction Calibration + Decision Replay** — trustworthy probabilities and reproducibility.
5. **Decision Quality Benchmark** — quantitative measurement of GuardAi value.
6. **Reusable AI Research Integration Gate** — audit and selectively integrate Gymnasium/PettingZoo/SB3/CleanRL/RL Zoo and other candidates.
7. **RL Environment Contract** — Gymnasium-based experiments with a separately validated training reward.
8. **Runtime hardening** — safety-first execution boundary and measured latency targets.

## 17. Long-term direction
NosAi/NosTale is the current reference project. A future game-agnostic platform may detect games, select adapters, auto-configure perception/reasoning/control and learn from play, but this remains a long-term direction rather than the current scope.

## 18. Architectural invariants
1. PlayAi and GuardAi retain their permanent identities.
2. GuardAi may challenge PlayAi; PlayAi is not automatically correct.
3. Decision Fabric is the arbitration/evidence layer, not the RL reward function.
4. Execution is separated from cognition by an authorization boundary.
5. External frameworks are optional and removable.
6. Benchmarks distinguish targets from measured results.
7. Significant architectural changes require reproducible evidence before promotion.
