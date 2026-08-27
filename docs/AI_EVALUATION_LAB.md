# NosAi AI Evaluation Lab — v2

## Purpose
The AI Evaluation Lab is the controlled offline/optional experimentation layer. It is not a runtime dependency and must never be required for the local game runtime, Safety Gate, CI or action transport.

## Architecture
```text
Scenario / Replay
      ↓
World-state fixture
      ↓
Candidate PlayAi policy / GuardAi policy / RL model
      ↓
Normalized decision + GuardAi verdict
      ↓
Decision Fabric evaluator
      ↓
Safety / constraints / latency / confidence / outcome
      ↓
Evidence → Dashboard / Regression / CI
```

## PlayAi vs PlayAi+GuardAi benchmark
Every important experiment should support paired evaluation:
1. PlayAi-only baseline.
2. PlayAi + GuardAi cooperation.
3. Optional alternative policy/model.

The same scenario, seed, action space and evaluation constraints should be used wherever possible. This allows the real value of GuardAi to be measured rather than assumed.

## Dynamic Decision Fabric evaluation
The Lab must test context-dependent weights, bounded latency penalty and hard-timeout behavior. It should record which evidence changed the final decision and whether GuardAi's intervention was beneficial, unnecessary or harmful.

## Operational decision vs RL reward
The evaluator keeps production decision scoring separate from training reward. RL experiments can consume derived signals such as progression, survival, risk, stale-state and time-budget penalties, but reward definitions remain independently versioned and benchmarked.

## Reusable AI research track
Evaluate external tooling here before it enters NosAi:
- Gymnasium environment compatibility;
- PettingZoo multi-agent scenarios for PlayAi/GuardAi;
- Stable-Baselines3 baseline experiments such as PPO;
- CleanRL algorithm cross-checks;
- RL Baselines3 Zoo configurations and benchmarks;
- Agent Lightning-inspired trajectory/reward experiments;
- game-agent repositories as architecture references;
- MALib only if distributed multi-agent complexity is justified by measured workload.

Each candidate requires a Third-Party Component Audit.

## Rules
1. External providers/frameworks are optional; NosAi must remain functional without them.
2. Credentials are never stored in fixtures, HTML, logs or committed datasets.
3. Evaluation inputs are sanitized fixtures or recorded observations, not live action commands.
4. The evaluator compares decisions; it does not execute game actions.
5. No result bypasses Planner, Decision Fabric or Safety Gate.
6. Results contain scenario id, candidate id, timestamp, evidence version and evaluation status.
7. Deterministic CI fixtures must not depend on network availability.
8. Framework adoption requires license, maintenance, dependency, security, API and performance review.
9. Performance values are labelled target until measured on the actual target configuration.

## Scenario schema
Required: `scenario_id`, `world_state`, `available_actions`, `constraints`, `expected_outcome` or constraints, `source`, `schema_version`.
Optional: `replay_id`, `tags`, `difficulty`, `notes`, `seed`.

## Result schema
Each result should contain `scenario_id`, `candidate_id`, `decision`, `confidence`, `status` (`PASS`, `FAIL`, `NOT_RUN`), `safety_status`, `latency_ms`, `reason_codes`, `evidence_version`, and where applicable `guardai_verdict`.

## Metrics
Primary metrics:
- decision accuracy against constraints;
- safety violation rate;
- invalid-action rate;
- goal completion rate;
- confidence calibration;
- p50/p95 decision latency;
- regression rate;
- RL reward, sample efficiency, stability and reproducibility;
- GuardAi intervention value;
- unnecessary GuardAi intervention rate;
- decision reversals;
- counterfactual improvement over the PlayAi baseline.

## Benchmark integrity
All reported performance numbers must include hardware configuration, workload, sample count, seed where relevant and methodology. A target such as `<2 ms` or `60 Hz` is not an achieved result until reproduced by the Test Center.

## Dashboard integration
Expose a read-only AI Lab view with scenario counts, candidate comparison, pass/fail/not-run totals, accuracy/safety trends, latency, baseline delta, RL metrics and evidence provenance. Live runtime controls remain outside the lab view.

## CI integration
CI runs deterministic local fixtures. External-model/framework evaluations are informative and become `NOT_RUN` when unavailable; they must not silently become `PASS`.

Recommended pipeline:
`fixtures → evaluator → JSON/JUnit evidence → Test Center → artifact`

## Implementation phases
1. Scenario/result schemas and validation.
2. Deterministic evaluator using the current NosAi baseline.
3. Dynamic Decision Fabric test suite.
4. Paired PlayAi vs PlayAi+GuardAi benchmark.
5. Dashboard read-only AI Lab view.
6. Replay comparison and regression fixtures.
7. Gymnasium/PettingZoo prototypes.
8. SB3 PPO baseline and CleanRL cross-check.
9. RL Zoo benchmark/configuration comparison.
10. Optional trajectory-level experiments inspired by Agent Lightning.
11. Third-party audit and promotion decision for each adopted component.

## Definition of Done
The research milestone is complete when deterministic scenarios run offline, PlayAi/GuardAi benefit is quantitatively measured, results are provenance-tagged, failures are visible in Test Center, targets are separated from measured results, candidate frameworks are audited, and no external provider is required to start or operate NosAi.
