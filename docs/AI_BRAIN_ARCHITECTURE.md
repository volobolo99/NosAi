# NosAi brain architecture — 4.21

## Goal

Turn NosAi from a collection of perception, strategy and learning utilities into a layered decision system that can improve from real episodes without coupling learning to client control.

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
 PlayAiGuardAiBridge
          |
       GuardAi
   /   |    |    \
Sim Prediction Risk Adversarial
          |
 Decision Fabric 2.0
          |
 Evaluation / reward -> Replay / episodes -> offline training
```

## Research adopted as design input

NosAi uses external projects as optional research/tooling inputs rather than replacing its own architecture.

- **Gymnasium**: environment API target for a future observation-only `NosTaleEnv`.
- **PettingZoo**: multi-agent environment patterns for explicit PlayAi/GuardAi cooperation and evaluation.
- **Stable-Baselines3**: optional PyTorch RL baseline, especially PPO experiments.
- **CleanRL**: readable reference implementations for inspecting and adapting individual algorithms.
- **RL Baselines3 Zoo**: reproducible experiment/configuration/benchmark reference.
- **Agent Lightning**: trajectory-level trace/reward architecture inspiration, without importing the whole framework.
- **Game-agent repositories**: perception/state/policy/reward pipeline references only.
- **MALib**: future multi-agent/distributed-learning candidate, activated only if benchmark evidence justifies its complexity.

## Integration principles

1. Core NosAi remains provider/framework neutral.
2. External frameworks are optional and must not be required by the local runtime.
3. Every candidate undergoes license, maintenance, API, dependency, security and performance audit.
4. Learning remains separated from client control.
5. Deterministic evaluation fixtures remain network-independent.
6. The smallest useful component is preferred over copying an entire framework.

## Vision roadmap

### Phase A — now

- deterministic strategic priors;
- confidence and risk estimates;
- episodic memory;
- persistent replay buffer;
- regression tests;
- research audit for reusable AI frameworks.

### Phase B — next

- Gymnasium-compatible `NosTaleEnv` in observation-only simulation mode;
- discrete action vocabulary and action masking;
- vector reward components;
- replay dataset/version metadata;
- baseline PPO experiment using optional Stable-Baselines3;
- multi-agent evaluation prototype using PettingZoo patterns.

### Phase C — advanced

- recurrent/transformer policy for temporal context;
- offline imitation learning;
- prioritized replay;
- curriculum over maps/rooms/objectives;
- uncertainty-aware policy selection;
- trajectory-level optimization;
- CleanRL reference comparisons;
- RL Zoo benchmark/configuration validation.

### Phase D — autonomy gate

Real-client execution remains behind explicit safety gates. Training, perception and decision evaluation must work without live input control. Only after the observation-only loop and safety/verification gates are stable should controlled action adapters be considered.

## Important rule

External projects are sources of implementation ideas and algorithms, not code to copy indiscriminately. Every adopted component must be checked for API compatibility, maintenance status, security, license compatibility and measurable benefit before becoming a runtime dependency.
