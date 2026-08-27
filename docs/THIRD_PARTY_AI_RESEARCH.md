# NosAi — Third-Party AI Research & Reuse Register

## Purpose

This document is the canonical register for reusable open-source AI/RL projects considered for NosAi. The goal is to obtain proven algorithms, interfaces, evaluation patterns and implementation ideas without replacing the NosAi architecture.

## Priority candidates

| Candidate | Role in NosAi | Adoption posture |
|---|---|---|
| Gymnasium | Standard environment interface; future `NosTaleEnv` target | Compatibility target / optional dependency |
| PettingZoo | Multi-agent environment patterns for PlayAi + GuardAi | High-priority evaluation integration |
| Stable-Baselines3 | PyTorch RL baselines, especially PPO | Optional experimental dependency |
| CleanRL | Readable RL algorithm implementations | Reference / cross-check |
| RL Baselines3 Zoo | Configurations and reproducible RL benchmarks | Benchmark/reference layer |
| Agent Lightning | Trajectory-level traces/reward and training separation concepts | Architecture reference |
| Game-agent repositories | Practical perception→state→policy→reward pipelines | Reference only; case-by-case audit |
| MALib | Multi-agent/distributed learning | Future candidate; only if justified by benchmarks |

## Why these projects fit NosAi

NosAi already separates perception/state, PlayAi reasoning, GuardAi supervision, Decision Fabric, memory/replay and evaluation. The projects above can strengthen those boundaries instead of forcing a monolithic agent design.

### PlayAi
Use RL libraries only for controlled policy experiments. PlayAi remains the primary strategic intelligence and owns the decision proposal contract.

### GuardAi
Use simulation, evaluation and multi-agent patterns to challenge PlayAi, quantify uncertainty and compare alternatives. GuardAi remains independent from any specific RL framework.

### Test Center / AI Evaluation Lab
This is the preferred location for external-framework experiments. Candidate policies are evaluated against deterministic fixtures and identical scenarios before any adoption decision.

## Third-Party Component Audit

Before code or a dependency is adopted, record:

1. repository and exact version/commit;
2. license and distribution compatibility;
3. maintenance/activity;
4. API compatibility;
5. Python/PyTorch/runtime compatibility;
6. dependency footprint;
7. security and supply-chain considerations;
8. CPU/GPU/RAM and latency overhead;
9. reproducibility;
10. test coverage and benchmark evidence;
11. architectural fit with Core/Adapter and Decision Fabric;
12. measurable benefit versus the existing NosAi baseline.

## Integration rules

- Do not copy an entire framework when a small interface or algorithm is sufficient.
- Keep external frameworks optional whenever possible.
- Do not make the local NosTale runtime depend on a cloud provider or external model.
- Keep training/evaluation separated from live control.
- Do not allow an external framework to bypass Planner, Decision Gate or Safety/Control Plane.
- Pin versions when a dependency becomes production-relevant and record provenance.
- Maintain an exit path so NosAi can remove a third-party dependency without redesigning Core.

## Planned evaluation sequence

```text
NosAi baseline
    ↓
Gymnasium environment contract
    ↓
PettingZoo PlayAi/GuardAi scenarios
    ↓
Stable-Baselines3 baseline (e.g. PPO)
    ↓
CleanRL cross-check
    ↓
RL Zoo benchmark/config comparison
    ↓
Decision Quality Benchmark
    ↓
Adoption decision
```

Agent Lightning-inspired trajectory experiments and MALib are later stages, activated only if the measured workload justifies them.

## Success criteria

A third-party component is accepted only when it provides a measurable improvement in at least one target dimension—decision quality, sample efficiency, prediction quality, simulation fidelity, evaluation coverage, development speed or reproducibility—without unacceptable complexity, resource cost, licensing constraints or architectural coupling.
