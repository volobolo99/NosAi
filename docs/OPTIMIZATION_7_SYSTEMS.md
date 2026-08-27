# NosAi — Optimization 7 Systems

This document defines the seven optimization systems approved for the next architecture cycle. They are design/implementation targets and are not considered production-complete until Test Center evidence promotes them.

## 1. Decision Fabric 3.0
Structured `DecisionCandidate` and `GuardVerdict` contracts. Dynamic context-dependent weights combine PlayAi confidence, GuardAi evidence, simulation, state confidence, memory reliability, risk, latency and compute budget. Outputs include decision, confidence, risk, evidence, rationale, deadline and fallback.

## 2. Counterfactual Decision Engine
For important decisions, generate and evaluate alternatives A/B/C… against the same state. GuardAi ranks counterfactuals and reports whether the selected PlayAi action remains optimal under the available model. Counterfactual results are stored for later analysis.

## 3. Cognitive Trace
Every significant decision receives a trace ID linking observation, state, PlayAi proposal, GuardAi review, simulations, predictions, risk, counterfactuals, Decision Fabric result, execution result and outcome. Traces are structured, privacy-conscious and replayable.

## 4. Decision Quality + GuardAi Value Added
Benchmark PlayAi-only versus PlayAi+GuardAi using identical scenarios. Track outcome, efficiency, risk, prediction calibration, resource/time usage, decision reversals, GuardAi intervention rate and harmful/unnecessary interventions. Define `GuardAi Value Added` as the measured delta attributable to supervision, not an assumed benefit.

## 5. Mutation / Adversarial Testing
Create controlled faults in state, predictions, confidence, plans and simulation evidence. Measure whether GuardAi and the Decision Gate detect and contain them. Mutation operators and expected detection behavior are versioned as Test Center fixtures.

## 6. Adaptive Compute
Choose the minimum computation required by the decision context. Fast path: PlayAi only. Normal path: PlayAi + GuardAi. Critical/uncertain path: GuardAi + simulations + counterfactuals. Compute Broker can select local acceleration or optional cloud resources according to latency, privacy, capacity and cost constraints.

## 7. Failure Taxonomy + Self-Improvement Loop
Classify failures as `PERCEPTION_ERROR`, `STATE_ERROR`, `PLANNING_ERROR`, `PREDICTION_ERROR`, `SIMULATION_ERROR`, `RISK_ERROR`, `GUARDAI_ERROR`, `DECISION_FABRIC_ERROR`, `EXECUTION_ERROR`, or `MEMORY_ERROR`. Aggregate failures to prioritize engineering work.

Self-improvement loop:
`PLAY → OBSERVE → DECIDE → GUARD → ACT → OUTCOME → REPLAY → EVALUATE → FIND_ERROR → GENERATE_CANDIDATE → SIMULATE → BENCHMARK → PROMOTE`

Candidates never modify production behavior directly. Promotion requires reproducible evidence, regression coverage and relevant safety gates.

## OpenAI integration policy
OpenAI may be used where it provides measurable value for strategic reasoning, difficult-state analysis, alternative generation, explanation or improvement proposals. Deterministic state, simulation, probability, risk, benchmarking and execution controls remain local/framework-neutral wherever practical.

Use structured outputs/contracts rather than free-form text at module boundaries. API credentials must never be committed to source, fixtures, documentation or logs. Runtime configuration must obtain secrets from the approved secret/environment mechanism.

OpenAI is an optional cognitive provider, not a single point of failure for the NosAi runtime.

## Test matrix
Each system requires:
- unit/contract tests;
- deterministic integration fixtures;
- regression tests;
- fault/mutation tests where applicable;
- performance measurements;
- paired PlayAi/GuardAi evaluation;
- replayability verification;
- explicit PASS/FAIL/NOT_RUN evidence.

## Promotion criteria
A feature is promoted only when it demonstrates measurable improvement or a verified architectural requirement without unacceptable regression in latency, reliability, safety or resource usage. Claimed performance values remain targets until measured on the target hardware/configuration.
