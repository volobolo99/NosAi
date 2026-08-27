# NosAi — Master Roadmap V4

Date: 2026-08-27
Branch: `develop/nosai-next`
Stable branch: `main`

## Architectural direction — CONFIRMED

NosAi is **offline-first and continually improving**. The gameplay core must remain usable without Internet. Online services feed an isolated Evolution Lab that researches, proposes and evaluates improvements. No Internet result or simulation result directly changes production.

`experience -> observation -> research -> candidate -> immutable payload -> Windows Sandbox -> replay -> regression -> anti-forgetting -> evidence -> staging -> real Windows -> real NosTale -> explicit confirmation -> consolidation`

## P0 — Evolution safety and evidence

| Work item | Status | Maturity |
|---|---|---:|
| REAL / CI / SIMULATED evidence separation | implemented | 90% |
| Research/candidate provenance | implemented | 85% |
| Promotion Firewall contract | implemented | 70% |
| Protected replay store | implemented | 70% |
| Anti-forgetting gate | implemented | 65% |
| Version/model/strategy registry contract | implemented | 60% |
| Patch evaluation gate | implemented | 70% |
| Sandbox request safety validation | hardened contract | 70% |
| Windows Sandbox CLI backend | implemented, host validation pending | 40% |
| Immutable runtime payload integrity verifier | implemented | 45% |
| Deterministic runtime manifest builder | implemented | 45% |
| Deterministic protected replay executor | implemented | 60% |
| Candidate regression suite | implemented | 55% |
| Integrated sandbox -> replay -> regression pipeline | implemented, host validation pending | 50% |
| Windows evidence schema/collector | implemented, real-host validation pending | 45% |
| Windows Sandbox CI gate | configured, self-hosted runner required | 35% |
| Prepared immutable Windows runtime payload | pending | 10% |
| Real Windows evidence collector validation | pending | 25% |
| Real NosTale evidence collector | pending | 15% |

Percentages are engineering maturity estimates, not test-pass claims. OS-level execution remains below production readiness until exercised on an actual supported Windows host with a prepared immutable payload. Evidence marked REAL must come from the real host; CI/SIMULATED results never get relabeled as REAL.

## P1 — Offline intelligence

1. `NosAiLLM` provider contract + local llama.cpp adapter.
2. Local memory/retrieval adapter and benchmark.
3. Stable-Baselines3 adapter and offline training/evaluation harness.
4. Continual-learning benchmark/replay stream.
5. Drift detection.
6. OpenTelemetry-compatible correlation.
7. Evolution dashboard with run/evidence drill-down.

## P2 — Scale and advanced capabilities

- optional vLLM server path;
- DVC for large model/dataset lineage where justified;
- advanced explainability;
- additional RL/continual-learning algorithms;
- additional online research providers.

## Release rule

`main` contains only explicitly confirmed versions. Promotion requires all applicable tests and runtime gates to be PASS, complete provenance, no release-blocking defect and explicit confirmation. Simulation PASS is never a substitute for real Windows/NosTale validation.
