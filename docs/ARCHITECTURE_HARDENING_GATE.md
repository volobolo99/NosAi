# NosAi Architecture Hardening Gate

## Five priority upgrades

1. **Decision Fabric 2.0** — evolve arbitration into a multi-evidence decision engine combining PlayAi proposals, GuardAi critique/prediction, simulation, World State confidence, memory evidence, risk, latency and compute budgets. Output must include decision, confidence, risk, evidence, reason, deadline and fallback.
2. **GuardAi Trigger + Risk Engine** — invoke deeper GuardAi analysis when risk, uncertainty, novelty, confidence gaps or decision cost justify it; decompose risk into failure, resource, time, unknown-state and execution dimensions.
3. **Temporal World Model** — evolve snapshots into a time-aware belief state using recent observations, changes, trends and anomalies while retaining provenance/confidence.
4. **Prediction Calibration + Decision Replay** — retain predictions and outcomes, measure calibration/error, and make important decisions reproducible from state, proposals, evidence, simulation seed and outcome.
5. **Decision Quality Benchmark** — compare PlayAi-only against PlayAi+GuardAi under identical scenarios and quantify success, survival, reward, time, resource efficiency, prediction accuracy and unnecessary interventions.

## Implementation rule

These upgrades must integrate with existing PlayAi, GuardAi, progression, Decision Fabric, Safety/Execution gates, Test Center and CI rather than creating parallel control paths. No component may bypass the existing execution authorization boundary.

## Promotion gate

Each upgrade requires unit/contract tests, integration tests, regression coverage and measurable benchmark evidence before promotion. Runtime integration remains observation-first until the relevant safety and verification gates are green.
