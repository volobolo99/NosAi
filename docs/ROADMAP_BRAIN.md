# NosAi — Brain Roadmap

## Mission
Build a modular, testable and progressively trainable NosTale AI. Keep perception, world state, strategy, learning and actuation separated so each layer can evolve independently.

## Execution order

### Phase 0 — Baseline and safety gate
- Freeze a known-good baseline.
- Inventory modules, dependencies, tests and CI.
- Define observation-only as the default runtime mode.
- Add deterministic fixtures for representative NosTale states.
- Gate: all existing tests pass; no live input/output is enabled accidentally.

### Phase 1 — Canonical world model
- Define versioned schemas for player, target, map/room, resources, combat, objectives and raid context.
- Normalize units and ranges.
- Add validation and missing/unknown-value semantics.
- Keep source provenance for every observation (API, vision, manual, inferred).
- Gate: identical observations produce identical normalized state.

### Phase 2 — Strategic brain
- Keep rule-based safety constraints deterministic.
- Add candidate action generation.
- Add scoring, confidence and reason codes.
- Integrate memory retrieval as evidence, never as an unchecked command.
- Gate: explainable decision traces and deterministic safety behavior.

### Phase 3 — Memory and experience substrate
- Episodic memory with bounded retention.
- Replay buffer with schema/version metadata.
- Outcome attribution and episode summaries.
- Similar-state retrieval and confidence calibration.
- Gate: persistence/recovery tests and no corrupted learning records.

### Phase 4 — Simulator / Gymnasium environment
- Implement a lightweight NosTale abstraction environment.
- Separate environment dynamics from the live adapter.
- Start with deterministic toy scenarios: movement, target selection, resource management, room objectives.
- Add stochasticity only after deterministic tests are stable.
- Gate: reset/step contract, reproducible seeds, reward accounting tests.

### Phase 5 — Offline learning
- Train from recorded/replayed trajectories before touching live control.
- Establish baselines: heuristic policy, behavior cloning where data exists, then PPO/other RL candidates.
- Track experiments, checkpoints and evaluation metrics.
- Gate: learned policy must beat baseline on held-out scenarios without violating safety constraints.

### Phase 6 — Perception
- Build screen capture as an isolated observation source.
- Add UI/state detectors and confidence scores.
- Add calibration for client position/ROI.
- Prefer deterministic CV for stable UI elements; use learned vision only where it materially improves robustness.
- Gate: measured detection accuracy and latency on recorded frames.

### Phase 7 — Planner and policy fusion
- Hierarchical decision loop: safety → objective → tactical planner → learned policy → action validation.
- Add action masking so impossible/unsafe actions cannot be selected.
- Add short-horizon planning for movement/combat objectives.
- Gate: policy cannot bypass safety or act on stale state.

### Phase 8 — Shadow mode
- Live perception + decision making, but no actuation.
- Compare decisions with human/operator outcomes.
- Log state, candidates, selected action, confidence, latency and reward proxy.
- Gate: stable performance across long sessions.

### Phase 9 — Controlled actuation
- Introduce a separate controller with explicit capability boundaries.
- Start with low-risk actions and manual emergency stop.
- Add rate limits, stale-state checks and fail-closed behavior.
- Gate: soak tests and emergency-stop validation.

### Phase 10 — Continuous improvement
- Automatic session reports.
- Failure clustering.
- Regression suite generated from real failures.
- Dataset curation and replay prioritization.
- Periodic retraining only after evaluation gates pass.

## Architecture rule
Do not make the LLM, RL policy, memory, vision model or game adapter the sole source of truth. The canonical world model and deterministic safety layer remain authoritative.

## Dependency policy
Use mature external projects as isolated dependencies or references. Prefer stable APIs and permissive licenses. Do not copy large codebases into NosAi when a clean dependency or small adapter is sufficient. Record attribution and license information for any reused code.

## Research shortlist
- Gymnasium: standard environment API for RL.
- Stable-Baselines3: reliable PyTorch RL implementations.
- SB3-Contrib: experimental RL algorithms.
- CleanRL: compact reference implementations.
- RL Baselines3 Zoo: training/evaluation patterns.
- PettingZoo: future multi-agent environment interface if team/raid learning requires it.
- OpenTelemetry: future standardized observability layer if current telemetry becomes insufficient.

## Definition of done
Every phase must have:
1. tests;
2. deterministic fixtures where applicable;
3. documentation;
4. measurable acceptance criteria;
5. no regression of earlier phases.
