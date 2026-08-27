# NosAi brain architecture — 4.22

## Goal
Turn NosAi into a layered decision system that improves from episodes without coupling learning to client control. **PlayAi** remains the primary intelligence; **GuardAi** remains the independent supervisory intelligence.

## Architecture
```text
NosTale observation adapter
          |
State normalization -> Temporal World Model
          |
     Strategic Brain
          |
       PlayAi
          |
Candidate plans / Action Intent
          |
 PlayAiGuardAiBridge
          |
       GuardAi
   /   |    |      |       \
Sim Prediction Risk Trigger Adversarial
          |
   APPROVE / MODIFY / REJECT / REQUEST_MORE_SIMULATION
          |
 Decision Fabric 2.0
          |
 Decision Gate -> Safety/Control Plane -> Execution boundary
          |
Outcome -> Replay / Memory -> Benchmark -> offline training
```

## Decision Fabric v3 principles
The baseline utility model is `U(a) = wp*C_PlayAi + ws*C_Sim - wr*R - wl*L`. The weights are **context-dependent**, not permanently fixed. Risk and latency are normalized/bounded; hard timeout is a deterministic gate condition. Decision output contains decision, confidence, risk, evidence, rationale, deadline and fallback.

GuardAi is a structured reviewer, not just a numeric feature. The Decision Fabric combines its verdict with simulation, prediction, state confidence, memory reliability, risk, latency and compute budget.

## Operational decision vs training reward
Operational Decision Fabric and RL reward remain separate contracts. Reward can derive evidence from risk, stale state, time budget, survival, efficiency and progression, but it must not become a rigid copy of the production decision formula. Reward definitions are experimental and validated through benchmark results.

## Research adopted as design input
NosAi uses external projects as optional research/tooling inputs rather than replacing its architecture.
- **Gymnasium**: environment API target for future observation-only `NosTaleEnv`.
- **PettingZoo**: multi-agent patterns for PlayAi/GuardAi cooperation and evaluation.
- **Stable-Baselines3**: optional PyTorch RL baseline, especially PPO experiments.
- **CleanRL**: readable algorithm references and independent cross-checks.
- **RL Baselines3 Zoo**: reproducible experiment/configuration/benchmark reference.
- **Agent Lightning**: trajectory-level trace/reward architecture inspiration.
- **Game-agent repositories**: perception/state/policy/reward pipeline references.
- **MALib**: future distributed multi-agent candidate only if benchmark evidence justifies complexity.

## Integration principles
1. Core NosAi remains provider/framework neutral.
2. External frameworks are optional and must not be required by the local runtime.
3. Every candidate undergoes license, maintenance, API, dependency, security and performance audit.
4. Learning remains separated from client control.
5. Deterministic evaluation fixtures remain network-independent.
6. Small useful components are preferred over whole-framework adoption.
7. Performance claims are marked as targets until measured on the actual target configuration.

## Roadmap
### Phase A — foundation
- deterministic strategic priors;
- confidence/risk estimates;
- episodic memory and replay;
- regression tests;
- dynamic Decision Fabric contract;
- reusable-AI research audit.

### Phase B — controlled RL
- Gymnasium-compatible observation-only `NosTaleEnv`;
- discrete action vocabulary and action masking;
- vector reward components;
- replay dataset/version metadata;
- baseline PPO using optional Stable-Baselines3;
- PettingZoo-style multi-agent evaluation.

### Phase C — advanced learning
- recurrent/transformer temporal policy;
- offline imitation learning;
- prioritized replay;
- curriculum over maps/rooms/objectives;
- uncertainty-aware policy selection;
- trajectory-level optimization;
- CleanRL cross-checks;
- RL Zoo benchmark/configuration validation.

### Phase D — autonomy gate
Real-client execution remains behind explicit safety gates. Training, perception and decision evaluation must work without live input control. Controlled action adapters are considered only after observation-only, verification and safety gates are stable.

## Performance validation
Targets such as `<2 ms` adapter latency or `60 Hz` decision throughput are hypotheses/targets until Test Center measurements establish them. Benchmarks must record hardware configuration, workload, sample count and methodology.

## Important rule
External projects are sources of implementation ideas and algorithms, not code to copy indiscriminately. Every adopted component must be checked for API compatibility, maintenance status, security, license compatibility, performance and measurable benefit before becoming a runtime dependency.
