# NosAi — Quantitative Progression Simulator

## Purpose

Define the deterministic/simulation layer used by GuardAi to compare character-progression plans without directly executing game actions.

## Inputs

- CharacterSnapshot version/hash
- current progression state
- target objective
- candidate plans
- known game rules/mechanics
- validated market data when applicable
- simulator version
- random seed
- confidence/data-quality metadata

## Core model

Each plan produces a distribution, not a single guessed outcome:

`PlanResult = { expected_progress, success_probability, time_distribution, resource_cost, risk, confidence }`

For stochastic activities, run repeated seeded simulations. Report mean/median and percentile bands; never present a point estimate as certainty.

## Utility

GuardAi ranks plans using configurable weights:

`utility = progress_gain * progress_weight + time_saved * time_weight - resource_cost * cost_weight - risk * risk_weight`

Policy-invalid plans are removed before utility ranking. User preferences may change weights, but cannot override safety/policy constraints.

## Scenario classes

1. baseline/current strategy;
2. candidate in-game strategy;
3. alternative progression path;
4. hypothetical external-resource scenario for analysis only when policy permits analysis;
5. hybrid/offline simulation scenario.

## Outputs

- recommended plan;
- alternatives;
- expected time-to-target;
- probability of reaching target by time budget;
- resource requirements;
- expected stat/progression delta;
- sensitivity analysis;
- confidence and data provenance;
- reasons for recommendation/rejection.

## Validation

- deterministic replay with fixed seed;
- monotonicity checks for resource/stat changes;
- impossible-state rejection;
- model/version hash;
- comparison against historical observations where available;
- regression suite for every simulator change.

## Guardrails

Simulation results are advisory evidence. They never directly authorize an action. Final execution remains subject to Decision Fabric, Safety Gate and Human Override.
