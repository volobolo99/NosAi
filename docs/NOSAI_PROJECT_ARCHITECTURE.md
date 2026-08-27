# NosAi — Project Architecture Map

## 1. Mission
NosAi is an AI system focused on playing NosTale through a cooperative architecture in which PlayAi is the primary agent and GuardAi is the independent supervisory intelligence. The project prioritizes reliability, measurable decisions, simulation, safety, testability and progressive runtime integration.

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
Safety / Control Plane
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
Primary intelligence. Interprets the current state, manages objectives, plans strategies, selects tactical approaches and produces action intents. It is the main decision-making agent and is not replaced by GuardAi.

### GuardAi
Secondary supervisory intelligence. Reviews PlayAi proposals, performs simulations and probability estimates, evaluates risk, searches for alternatives and can reject or challenge a proposal. It should intervene more deeply when risk, uncertainty, novelty or confidence gaps justify the compute cost.

### Decision Fabric
The arbitration/cooperation layer. It combines evidence rather than simply selecting between two proposals: PlayAi proposal, GuardAi critique/prediction, simulation, World State confidence, memory evidence, risk, latency and compute budgets. Its output should explain the chosen decision, confidence, risk, evidence, reason, deadline and fallback.

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

## 7. Memory and learning

Intelligent Memory, Memory Reliability Layer, Counterfactual Memory and Improvement Candidates provide evidence-backed experience. Proposed changes must pass simulation, regression, benchmarks and promotion gates.

## 8. Decision lifecycle

```text
Observation -> normalization -> state confidence -> PlayAi proposal
-> GuardAi review -> simulation/prediction/risk -> Decision Fabric
-> Decision Gate -> Safety/Control Plane -> execution boundary
-> outcome -> replay/memory -> benchmark/learning
```

No cloud result, recommendation, simulation or memory may bypass the execution authorization boundary.

## 9. Decision Replay and Test Center

Important decisions are reproducible from Decision ID, state, proposals, evidence, memory references, simulation seed, Decision Fabric result and outcome. Test Center covers unit/contract, integration, E2E fixtures, regression, fault injection, simulation validation, performance, decision quality and safety boundaries.

## 10. Reusable AI research layer

External projects are treated as **research inputs and optional tooling**, not as wholesale replacements for NosAi. The first candidates are:

- **Gymnasium** — standard environment API and a natural target for a future observation-only NosTale training environment.
- **PettingZoo** — multi-agent environment patterns relevant to formalizing PlayAi/GuardAi cooperation and evaluation.
- **Stable-Baselines3** — optional PyTorch RL implementations for controlled experiments such as PPO; never a hard runtime dependency.
- **CleanRL** — readable algorithm references for understanding and adapting individual RL methods.
- **RL Baselines3 Zoo** — benchmark/configuration reference for reproducible RL experiments.
- **Agent Lightning** — architectural inspiration for trajectory-level traces/rewards and training decoupled from runtime agents.
- **Game-agent projects** — practical perception→state→policy→action→reward pipelines used only as reference patterns.
- **MALib** — future research candidate for multi-agent/distributed learning if the evaluation workload justifies it.

### Adoption rule
Before any dependency becomes part of NosAi, perform a Third-Party Component Audit covering license, maintenance, API compatibility, Python/PyTorch compatibility, security, size/overhead, reproducibility and architectural fit. Prefer small, optional integrations over framework replacement.

## 11. Compute architecture

Local Compute, External SSD, Compute Broker and cloud tiers remain part of the infrastructure roadmap. RL/training workloads may use optional acceleration, while the local game runtime must remain functional without external providers.

## 12. Dashboard

The operational cockpit exposes PlayAi objective/plan/confidence, GuardAi risk/prediction/simulation/recommendation, Decision Fabric rationale, World State, memory evidence, hardware and local/cloud usage, Test Center, AutoConfig and gate status. Add an AI Research/Evaluation view for benchmark comparisons and provenance.

## 13. CI and promotion

CI is a hard evidence gate: dependency integrity, static checks, imports, tests, security checks and relevant Test Center suites. External-model evaluations are informative and must not silently become PASS when unavailable.

## 14. Priority hardening gate

1. Decision Fabric 2.0.
2. GuardAi Trigger + Risk Engine.
3. Temporal World Model.
4. Prediction Calibration + Decision Replay.
5. Decision Quality Benchmark.
6. **Reusable AI Research Integration Gate** — audit Gymnasium/PettingZoo/SB3/CleanRL/RL Zoo and integrate only the smallest justified components.

## 15. Development principle

```text
ANALYZE -> DESIGN -> IMPLEMENT -> TEST -> INTEGRATE -> VERIFY
-> BENCHMARK -> CORRECT -> RE-VERIFY -> PROMOTE
```

No component is production-ready merely because it compiles. NosAi favors measurable evidence, reproducibility, safety boundaries, modularity and continuous improvement.

## 16. Long-term vision

NosAi/NosTale is the current reference project. A future game-agnostic platform may detect games, select adapters, auto-configure perception/reasoning/control and learn from play, but this remains a long-term direction rather than the current scope.
