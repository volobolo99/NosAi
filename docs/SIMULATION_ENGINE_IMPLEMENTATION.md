# NosAi Simulation Engine — implementation mapping

This document records the implementation of the supplied `NosAi Technical Architecture Specification` (v2.4-PROD, 28 August 2026) without changing the existing client safety boundary.

## Implemented

- **EKF state fusion**: `app/simulation/ekf.py` provides predict/update/step operations, diagonal covariance and configurable state transition. The implementation is dependency-free and can consume normalized adapter observations.
- **Combat chain**: `app/simulation/combat.py` implements morale-adjusted hit probability, shell penetration, elemental/fairy calculation, resistance reduction, critical/S-damage multipliers and bounded stochastic variance. A miss returns immediately with zero damage.
- **BCard FSM**: hard CC, stat-debuff replacement/max-level behavior, DoT lifetime and cleanse-by-level are represented explicitly.
- **Dynamic path planning**: `app/simulation/pathfinding.py` implements weighted A* over a costmap containing AoE, aggro-overlap and LoS-block costs. The planner boundary is compatible with a later hierarchical A* backend.
- **50 Hz / 120 s black box**: `TelemetryBuffer` defaults to 6,000 samples and therefore models the specified 120-second window at 50 Hz.
- **RCA**: `PostMortemRCA.first_divergence()` identifies the first sample whose Euclidean real-vs-simulated state error exceeds epsilon. `bayesian_update()` provides the discrete posterior update primitive for parameter hypotheses.
- **Make-or-Buy**: `app/simulation/economy.py` implements geometric expected attempts, 90% confidence attempt count, expected/worst make cost and NosBazar comparison. The EUR conversion is treated strictly as valuation; no external RMT transaction is executed or facilitated.

## Safety and source-of-truth boundaries

The supplied specification is source-derived engineering input. The runtime does not treat unverified game mechanics as facts, and it does not bypass the existing observation-only client boundary. The repository README states that live integration requires an explicit adapter and that the current concrete Windows adapter is observation-only.

The current implementation therefore exposes pure simulation primitives. Connecting them to live state remains an integration step requiring validated observations and existing pre-flight checks.

## Validation

`tests/test_simulation_engines.py` covers the critical invariants: miss short-circuiting, positive hit damage, BCard priority behavior, EKF convergence toward observations, geometric make-or-buy math, hazard-aware routing and RCA/Bayesian updates.
