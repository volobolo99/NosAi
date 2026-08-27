# NosAi — Project Architecture Map

## 1. Mission
NosAi is an AI system focused on playing NosTale through a cooperative architecture in which PlayAi is the primary agent and GuardAi is the independent supervisory intelligence. The project prioritizes reliability, measurable decisions, simulation, safety, testability and progressive runtime integration.

## 2. High-level architecture

```text
                           NOSAI
                             |
        +--------------------+--------------------+
        |                                         |
   PERCEPTION / STATE                        AI COGNITION
        |                                         |
  World State                                  PlayAi
        |                                         |
  CharacterSnapshot                              |
        |                                  candidate plans
        +--------------------+--------------------+
                             |
                    PlayAiGuardAiBridge
                             |
                          GuardAi
                +------------+-------------+
                |            |             |
            Simulator    Prediction      Risk
                |            |             |
                +------------+-------------+
                             |
                    Decision Fabric 2.0
                             |
                      Decision Gate
                             |
                    Safety / Control Plane
                             |
                         Executor
                             |
                         NosTale
                             |
                         outcome
                             |
                +------------+-------------+
                |                          |
              Memory                    Replay
                |                          |
                +------------+-------------+
                             |
                    Learning / Improvement
                             |
                         Test Center
                             |
                    CI / Quality Gates
```

## 3. Core identity

### PlayAi
Primary intelligence. Interprets the current state, manages objectives, plans strategies, selects tactical approaches and produces action intents. It is the main decision-making agent and is not replaced by GuardAi.

### GuardAi
Secondary supervisory intelligence. Reviews PlayAi proposals, performs simulations and probability estimates, evaluates risk, searches for alternatives and can reject or challenge a proposal. It should intervene more deeply when risk, uncertainty, novelty or confidence gaps justify the compute cost.

### Decision Fabric
The arbitration/cooperation layer. It should combine evidence rather than simply select between two proposals: PlayAi proposal, GuardAi critique/prediction, simulation, World State confidence, memory evidence, risk, latency and compute budgets. Its output should explain the chosen decision, confidence, risk, evidence, reason, deadline and fallback.

## 4. Perception and state

### World State
Read-only representation of the observed game/runtime state. It is the source layer from which normalized state is derived.

### CharacterSnapshot
Normalized structured state of the character and relevant environment. It carries observed facts plus confidence/provenance and is the stable contract between runtime observation and reasoning.

### Temporal World Model
Planned evolution beyond isolated snapshots. It maintains recent observations, state changes, trends and anomalies to create a current belief state.

### NosTale Adapter
Game-specific boundary under `app/adapters/`. It translates NosTale/runtime observations into the generic core contract. The current first boundary is observation-only; action/trade/purchase capabilities remain disabled at this layer.

### Generic Core / Adapter boundary
`app/core/adapter.py` defines the game-agnostic adapter contract and `WorldObservation`. This is intentionally small so future generalization does not slow NosAi.

## 5. Reasoning and planning

### Goal Manager
Maintains long-term objectives and priorities.

### Strategy / Planner
Transforms long-term objectives into mid-term plans, current objectives and tactical decisions.

### Action Intent
The output of PlayAi should express what it intends to accomplish before any concrete execution mechanism is selected.

### Progression Advisor
Analyzes character state and candidate progression plans, including bottlenecks, expected progress, time, cost and risk.

### Bottleneck Detector
Planned specialization that identifies root causes limiting progression instead of merely describing symptoms.

## 6. GuardAi intelligence

### Simulation Engine
Runs candidate strategies against a model of the state and estimates possible futures.

### Digital-Twin-style Simulator
Planned evolution of the simulator into a simplified game-world model covering combat, movement, resources, cooldowns, status effects, objectives and uncertainty.

### Prediction Engine
Produces success/failure probabilities and other forecasts used by GuardAi and Decision Fabric.

### Prediction Calibration
Records predictions versus actual outcomes and measures prediction error/calibration so GuardAi learns how reliable its confidence is.

### Risk Engine
Decomposes risk into relevant dimensions such as objective failure, resource loss, time loss, unknown-state risk and execution risk.

### GuardAi Trigger Engine
Determines when deeper GuardAi analysis is worth its computational cost using risk, uncertainty, novelty, confidence gaps, time pressure and previous failures.

### Adversarial Review
GuardAi actively tries to disprove or improve PlayAi's proposed plan rather than simply approving it.

## 7. Memory and learning

### Intelligent Memory
Stores useful experience and evidence for future decisions.

### Memory Reliability Layer
Each important memory should carry source, confidence, age, success/failure history and verification information so stale or weak evidence does not receive the same weight as repeatedly verified experience.

### Counterfactual Memory
Stores simulated alternatives when available: what happened with the selected strategy and what the simulator estimated for rejected alternatives.

### Improvement Candidates
NosAi can identify weaknesses and propose improvements, but changes must pass simulation, regression, benchmarks and promotion gates before becoming production behavior.

## 8. Decision lifecycle

```text
Observation
   -> normalization
   -> state confidence
   -> PlayAi proposal
   -> GuardAi review
   -> simulation/prediction/risk
   -> Decision Fabric
   -> Decision Gate
   -> Safety/Control Plane
   -> execution boundary
   -> observed outcome
   -> replay/memory
   -> benchmark/learning
```

Important rule: cloud results, GuardAi recommendations, simulations and memories must never directly bypass the execution authorization boundary.

## 9. Decision confidence

Confidence should be decomposed into:
- perception confidence;
- World State confidence;
- PlayAi confidence;
- GuardAi confidence;
- prediction confidence;
- simulation confidence;
- final decision confidence.

This prevents a highly confident decision from hiding weak underlying observations.

## 10. Decision Replay

Important decisions should be reproducible from a Decision ID, World State, PlayAi proposal, GuardAi analysis, evidence, memory references, simulation seed, Decision Fabric result and actual outcome. Replay is used for debugging, regression and learning.

## 11. Test Center

The Test Center is not only a unit-test collection. It should progressively provide:
- unit and contract tests;
- PlayAi/GuardAi integration tests;
- E2E fixtures;
- runtime-like scenarios;
- regression tests;
- fault injection;
- simulation validation;
- performance benchmarks;
- decision-quality benchmarks;
- safety-boundary tests.

### Decision Quality Benchmark
Compare PlayAi-only against PlayAi+GuardAi on identical scenarios using success, survival, reward, time, resource efficiency, prediction accuracy, decision reversals and unnecessary GuardAi interventions.

## 12. Control Plane and safety

The Control Plane coordinates lifecycle states and promotion. Safety/Execution gates remain separate from cognitive recommendations. No AI component should directly authorize or perform an action by bypassing these controls.

## 13. Compute architecture

### Local Compute
Uses the user's CPU/GPU/RAM and can be optimized through hardware benchmarking and AutoConfig.

### External SSD
Designed as portable storage for local models, caches, data and runtime assets where appropriate. It should not be treated as a substitute for compute.

### Compute Broker
Selects local/accelerated/cloud execution when useful, considering latency, capability, privacy and compute cost.

### Cloud tiers
The broader roadmap includes recommending free, economical and pro compute options and estimating expected performance impact. Recommendations must be based on current measured workload requirements rather than fixed claims.

## 14. Dashboard

The dashboard is the operational cockpit. It should expose:
- PlayAi current objective/plan/confidence;
- GuardAi risk/prediction/simulation/recommendation;
- Decision Fabric rationale and evidence;
- World State and anomalies;
- memory evidence;
- CPU/GPU/RAM and local/cloud usage;
- latency and performance;
- Test Center status;
- AutoConfig/benchmark controls;
- diagnostics and gate status.

The key UX question is: **why is NosAi doing this now?**

## 15. CI and promotion

CI is a hard evidence gate. Changes should pass dependency integrity, static checks, imports, unit/integration tests, security checks and relevant Test Center suites before promotion. A green code change is not assumed merely because it was written.

## 16. Current architecture strategy

NosAi remains fully focused on NosTale. The small generic Core/Adapter boundary is present only to prevent game-specific coupling from spreading. The future game-agnostic platform is a long-term possibility, not a current development target.

## 17. Priority hardening gate

The five highest-priority architectural improvements are:

1. Decision Fabric 2.0.
2. GuardAi Trigger + Risk Engine.
3. Temporal World Model.
4. Prediction Calibration + Decision Replay.
5. Decision Quality Benchmark.

They must integrate with existing components rather than create competing control paths.

## 18. Current development principle

```text
ANALYZE
  -> DESIGN
  -> IMPLEMENT
  -> TEST
  -> INTEGRATE
  -> VERIFY
  -> BENCHMARK
  -> CORRECT
  -> RE-VERIFY
  -> PROMOTE
```

No component is considered production-ready merely because it compiles. NosAi should favor measurable evidence, reproducibility, safety boundaries, modularity and continuous improvement.

## 19. Long-term vision

The future possibility is a general AI gaming platform that detects games, selects an adapter, auto-configures perception/reasoning/control and learns from play. NosAi/NosTale is the current primary project and reference environment for developing those reusable architectural patterns.
