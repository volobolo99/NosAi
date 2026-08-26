# NosAi brain architecture — 4.21

## Goal

Turn NosAi from a collection of perception, strategy and learning utilities into a layered decision system that can improve from real episodes without coupling learning to client control.

## Architecture

```text
NosTale client / observation adapter
              |
              v
      State normalization
              |
              v
     +-------------------+
     | Strategic Brain   |
     | safety            |
     | objective         |
     | urgency/risk      |
     | memory evidence   |
     +---------+---------+
               |
        BrainDecision
               |
       +-------+-------+
       |               |
   deterministic    future policy
     fallback       learner / RL
       |               |
       +-------+-------+
               v
        Evaluation / reward
               |
               v
        Replay / episodes
               |
               +----> offline training
```

## Why this design

The current repository already has a provider-neutral evaluation layer and a client adapter boundary. The new brain therefore produces a structured decision and never presses keys or clicks the game itself.

The memory/replay layer keeps experience separate from policy code. This allows experiments with PPO/DQN or other offline learners without rewriting the state model.

## Research adopted as design input

- **Gymnasium** provides a stable environment interface (`reset`, `step`, termination/truncation) and is the natural compatibility target for a future NosTale training environment. The project is actively maintained and currently lists release 1.3.0. [Farama Foundation, Gymnasium](https://github.com/Farama-Foundation/Gymnasium).
- **Stable-Baselines3** provides reliable PyTorch implementations of PPO and other RL algorithms. NosAi exposes these only as an optional dependency set so the core remains lightweight. [DLR-RM, Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3).
- **CleanRL** is useful as a reference when we need to inspect an algorithm implementation line-by-line; it intentionally favors readable single-file implementations over a large abstraction stack. [CleanRL](https://github.com/vwxyzjn/cleanrl).
- **Agent Lightning** demonstrates a useful trajectory-level training architecture: collect structured traces/rewards, store them, and let a trainer optimize agents without rewriting the runtime agent. We use this as architectural inspiration rather than importing the whole framework into NosAi. [Microsoft Agent Lightning](https://github.com/microsoft/agent-lightning).
- **Game-agent projects** such as Geometry Dash and Clash Royale show the practical pipeline we want: screen capture -> object/state extraction -> normalized state -> policy -> action -> reward/replay. These are references, not dependencies, and their assumptions must not be copied blindly into NosTale.

## Vision roadmap

The next perception layer should be:

1. screen/window capture,
2. ROI management for the user-selected NosTale client window,
3. OCR/template detection for UI values,
4. object detection for characters, mobs, loot and interactive objects,
5. temporal smoothing/tracking,
6. normalized state vectors consumed by the brain.

`mss` and OpenCV are exposed as optional dependencies for this direction. YOLO/Ultralytics is deliberately not a core dependency: its model/tool licensing must be reviewed for the intended distribution before it is embedded in the product.

## Learning roadmap

### Phase A — now

- deterministic strategic priors,
- confidence and risk estimates,
- episodic memory,
- persistent replay buffer,
- regression tests.

### Phase B — next

- Gymnasium-compatible `NosTaleEnv` in observation-only simulation mode,
- discrete action vocabulary and action masking,
- vector reward components instead of one opaque scalar,
- replay dataset/version metadata,
- baseline PPO experiment.

### Phase C — advanced

- recurrent/transformer policy for temporal context,
- offline imitation learning from human demonstrations,
- prioritized replay,
- curriculum over maps/rooms/objectives,
- uncertainty-aware policy selection,
- trajectory-level optimization and automatic regression discovery.

### Phase D — autonomy gate

Real-client execution must remain behind explicit safety gates. Training, perception and decision evaluation should work without live input control. Only after the observation-only loop is stable should an action adapter be enabled.

## Important rule

External projects are sources of implementation ideas and algorithms, not code to copy indiscriminately. Every adopted component must be checked for API compatibility, maintenance status, security, and license compatibility before becoming a runtime dependency.
