
# Nos AI v4.4 — StrategySimulator

v4.4 is a clean unified continuation of v4.3.2.

## New components

- `StrategySimulator`
- `TransitionModel`
- simulation state/action/outcome models
- deterministic sandbox scenario
- `StrategySimulatorBridge`
- unit and integration tests

## Decision flow

World State
    -> Goal
    -> Candidate Strategies
    -> StrategySimulator
    -> Expected outcome
    -> StrategyEngine / scorer
    -> Selected Plan

The simulator is deliberately separated from live execution. It predicts
candidate outcomes in a deterministic sandbox/replay model and does not
directly control a live game client.

This allows PvP/PvM/EXP/quest/item strategies to be compared using:
- success probability
- expected reward/progress
- expected duration
- expected risk

Future scenario adapters can implement richer state transitions while keeping
the simulator interface unchanged.
