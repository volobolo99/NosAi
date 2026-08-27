# NosAi — Project Architecture Map

## 1. Mission
NosAi is a fully local-first AI system focused on NosTale through a cooperative architecture in which **PlayAi** is the primary agent and **GuardAi** is the independent supervisory intelligence. The project prioritizes reliability, measurable decisions, simulation, safety, testability and progressive runtime integration.

## 2. High-level architecture
```text
Observation / NosTale Adapter
          |
World State -> CharacterSnapshot -> Temporal World Model
          |
        PlayAi
          |
Candidate Plans / Action Intent
          |
PlayAiGuardAiBridge
          |
        GuardAi
   +------+------+------+------+
   |      |      |      |      |
Simulator Prediction Risk Trigger Adversarial Review
          |
Decision Fabric 3.0
          |
Decision Gate
          |
Execution Safety Monitor
          |
Execution Policy / Executor
          |
Outcome -> Memory + Replay + Cognitive Trace
          |
Test Center / Benchmark / Learning
```

## 3. Local-only principle
**NosAi must operate without paid APIs, cloud inference or internet access at runtime.** OpenAI/cloud providers are not runtime dependencies for the current project phase. Any future provider integration is optional research only and must never be required for startup, reasoning, testing or execution.

## 4. Target local hardware profile
The reference development machine is the user's Acer Nitro V16 AI laptop. Exact hardware is detected by AutoConfig at runtime rather than hard-coded. The Nitro V16 family includes configurations with NVIDIA GPUs and Ryzen AI/NPU; for example, Acer documents an RTX 4060 8 GB configuration with Ryzen 7 8845HS and 16 TOPS NPU, while other V16 AI configurations differ. Therefore NosAi must benchmark the actual installed GPU/VRAM/RAM/CPU rather than assume a particular SKU.

## 5. Local AI Runtime
Use a local model runner abstraction. **llama.cpp** is the primary reference backend because it supports local GGUF models, quantization, NVIDIA CUDA, CPU+GPU hybrid inference and an OpenAI-compatible local server interface. The local provider must remain behind `LocalAIProvider` so the rest of NosAi does not depend on one runtime.

Recommended local model tiers are selected by benchmark, not by model name alone:
- **Fast model:** small quantized model for routine classification, extraction and simple reasoning.
- **Reasoning model:** medium quantized model for PlayAi/GuardAi strategic analysis.
- **Heavy model:** larger quantized model used only when Adaptive Compute determines the quality gain justifies VRAM/RAM/latency cost.

Models are stored locally (preferably on the external 2 TB SSD) while active model weights are loaded into RAM/VRAM as appropriate. Quantization is a first-class optimization.

## 6. PlayAi / GuardAi
### PlayAi
Primary intelligence: objectives, planning, strategy, candidate actions and action intents.

### GuardAi
Independent supervisory intelligence: simulation, prediction, probability, risk, alternative strategies and adversarial review. Structured verdicts: **APPROVE / MODIFY / REJECT / REQUEST_MORE_SIMULATION**.

## 7. Decision Fabric 3.0
Baseline:
`U(a) = wp*C_PlayAi(a) + ws*C_Sim(a) - wr*R(a) - wl*L(a)`

Weights are dynamic and context-dependent. Risk is decomposed into loss, time, uncertainty and execution risk. Latency penalty is bounded; hard timeout is a deterministic gate condition.

Decision input includes PlayAi proposal, GuardAi evidence, simulation/prediction, state confidence, memory reliability, risk, latency and compute budget. Decision output includes decision, confidence, risk, evidence, rationale, deadline and fallback.

## 8. Counterfactual Decision Engine
Important decisions can branch into A/B/C alternatives and be evaluated against the same state/model. GuardAi ranks counterfactuals and records whether the selected action remains optimal under available evidence.

## 9. Adaptive Compute
Local compute is allocated by decision difficulty:
- Fast: PlayAi/local small model.
- Normal: PlayAi + GuardAi.
- Critical/uncertain: GuardAi + simulations + counterfactuals + heavier local model.

Adaptive Compute must protect gaming/runtime responsiveness through budgets, queues, cancellation and fallback. It may move work between CPU, GPU and NPU when benchmark evidence supports it, but it does not use paid cloud inference.

## 10. Cognitive Trace
Every significant decision receives a trace ID linking observation, state, PlayAi proposal, GuardAi review, simulations, predictions, risk, counterfactuals, Decision Fabric result, execution result and outcome. Traces remain local and can be replayed for debugging/benchmarking.

## 11. Memory and learning
Intelligent Memory, Memory Reliability, Counterfactual Memory and Improvement Candidates remain evidence-backed. Self-improvement produces candidate changes; it does not directly modify production behavior.

## 12. Failure Taxonomy
Classify failures as:
`PERCEPTION_ERROR`, `STATE_ERROR`, `PLANNING_ERROR`, `PREDICTION_ERROR`, `SIMULATION_ERROR`, `RISK_ERROR`, `GUARDAI_ERROR`, `DECISION_FABRIC_ERROR`, `EXECUTION_ERROR`, `MEMORY_ERROR`.

Aggregated failure statistics determine the next optimization target.

## 13. Mutation / Adversarial Testing
Test Center injects controlled errors into state, predictions, confidence, plans and simulation evidence and verifies that GuardAi/Decision Gate detects or contains them.

## 14. Decision Quality Benchmark
Compare PlayAi-only against PlayAi+GuardAi on identical scenarios. Track success, survival, reward, efficiency, resource/time usage, calibration, reversals, intervention value and unnecessary/harmful interventions. `GuardAi Value Added` is measured, not assumed.

## 15. Operational Decision Fabric ≠ RL Reward
The production decision function and RL reward remain separate contracts. Local RL experiments may derive reward signals from progression, risk, stale state, time, survival and efficiency, but reward is independently versioned and validated.

## 16. Local RL / Research Stack
External projects are optional development tooling, not runtime cloud dependencies:
- Gymnasium — local environment API.
- PettingZoo — local multi-agent evaluation patterns.
- Stable-Baselines3 — local RL baseline experiments.
- CleanRL — local algorithm cross-checks.
- RL Baselines3 Zoo — reproducible benchmark/configuration reference.
- Agent Lightning — local research inspiration for trajectory-level training.
- MALib — only if local distributed experiments justify it.

## 17. Local storage architecture
The external 2 TB SSD is used for local models, datasets, replays, traces, caches, benchmark artifacts and optional training checkpoints. It provides storage/portability, not compute. NosAi should support a portable project bundle with model manifests and machine-specific AutoConfig.

## 18. Dashboard
Dashboard exposes PlayAi, GuardAi, Decision Fabric, Cognitive Trace, hardware utilization, local model selection, VRAM/RAM pressure, Adaptive Compute mode, benchmark results, AutoConfig and Test Center status. Cloud controls remain disabled in the current local-only phase.

## 19. Execution boundary
`Action Intent → Execution Policy → Execution Safety Monitor → Input Adapter → Executor/Runtime`.

No AI model may bypass Decision Gate or Safety/Control Plane.

## 20. Self-Improvement Loop
`PLAY → OBSERVE → DECIDE → GUARD → ACT → OUTCOME → REPLAY → EVALUATE → FIND_ERROR → GENERATE_CANDIDATE → SIMULATE → BENCHMARK → PROMOTE`.

Promotion requires reproducible evidence, regression tests and relevant safety gates.

## 21. Performance rules
Targets such as `<2 ms`, `60 Hz` or model-specific throughput are targets until measured on the actual Nitro configuration. AutoConfig/Benchmark must record CPU, GPU, VRAM, RAM, power mode, model, quantization, context, workload, sample count and methodology.

## 22. Current architecture hardening priorities
1. Decision Fabric 3.0.
2. Counterfactual Engine.
3. Cognitive Trace.
4. Decision Quality + GuardAi Value Added.
5. Mutation/Adversarial Testing.
6. Adaptive Compute.
7. Failure Taxonomy + gated Self-Improvement.
8. Local model runtime + model benchmark matrix.
9. Local RL environment and training pipeline.
10. Portable SSD + AutoConfig packaging.

## 23. Long-term direction
NosAi remains focused on NosTale. A future game-agnostic platform may reuse the Core/Adapter architecture, but this remains outside the current implementation target.

## 24. Architectural invariants
1. PlayAi and GuardAi retain their permanent identities.
2. GuardAi can challenge PlayAi; PlayAi is not automatically correct.
3. Everything required for current runtime operation is local.
4. External APIs/cloud providers are optional and disabled by default.
5. Execution is separated from cognition by an authorization boundary.
6. Benchmarks distinguish targets from measured results.
7. Significant changes require reproducible evidence before promotion.
