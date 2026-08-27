# NosAi Architecture Hardening Gate — v3

## Priority upgrades
1. **Dynamic Decision Fabric 2.0** — multi-evidence engine with context-dependent weights combining PlayAi proposal, GuardAi verdict/prediction, simulation, state confidence, memory evidence, risk, latency and compute budget.
2. **GuardAi Trigger + Risk Engine** — invoke deeper GuardAi analysis when risk, uncertainty, novelty, confidence gaps or decision cost justify it.
3. **Temporal World Model** — evolve snapshots into a time-aware belief state.
4. **Prediction Calibration + Decision Replay** — retain predictions/outcomes, measure calibration/error and make decisions reproducible.
5. **Decision Quality Benchmark** — compare PlayAi-only against PlayAi+GuardAi under identical scenarios.
6. **Reusable AI Research Integration Gate** — evaluate Gymnasium, PettingZoo, Stable-Baselines3, CleanRL, RL Baselines3 Zoo, Agent Lightning-inspired patterns and future MALib/game-agent references.
7. **RL Environment Contract** — keep Gymnasium/training reward independent from the operational Decision Fabric formula.
8. **Execution Hardening** — keep Action Intent, Safety Monitor, Execution Policy and Executor separated from cognition.

## Decision Fabric acceptance criteria
- dynamic weights are deterministic for a given context/version;
- latency penalty is bounded;
- hard timeout is a deterministic gate condition;
- GuardAi supports structured verdicts: APPROVE/MODIFY/REJECT/REQUEST_MORE_SIMULATION;
- decision output contains decision, confidence, risk, evidence, rationale, deadline and fallback;
- replay can reproduce important decisions.

## Research integration policy
External repositories are research inputs and optional tooling, not replacements for NosAi Core. Before adoption, record license compatibility, maintenance status, API fit, Python/PyTorch compatibility, security, resource overhead, reproducibility, test coverage and measured benefit.

Preferred order:
1. Gymnasium compatibility target;
2. PettingZoo multi-agent evaluation patterns;
3. Stable-Baselines3 optional baseline experiments;
4. CleanRL algorithm cross-checks;
5. RL Baselines3 Zoo benchmark/configuration references;
6. Agent Lightning trajectory/reward concepts where justified;
7. MALib only if distributed multi-agent experiments prove necessary.

## Benchmark integrity
Numbers such as `<2 ms` adapter latency or `60 Hz` decision throughput are targets until Test Center measurements reproduce them on the target configuration. Every benchmark records hardware, workload, sample count, seed where relevant and methodology.

## Implementation rule
All upgrades integrate with existing PlayAi, GuardAi, progression, Decision Fabric, Safety/Execution gates, Test Center and CI. No component may create a competing control path or bypass the execution authorization boundary.

## Promotion gate
Each upgrade requires unit/contract tests, integration tests, regression coverage and measurable benchmark evidence. External frameworks remain optional until their audit and benchmark gates are green. Runtime integration remains observation-first until the relevant safety and verification gates are green.
