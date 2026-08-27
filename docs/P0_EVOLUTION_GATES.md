# NosAi P0 Evolution Gates

This document defines the first hardening block of the offline-first Evolution Lab.

## Objective

Turn research and generated candidates into **measurable evidence** without allowing unverified code, knowledge or policies to enter the production gameplay core.

## Gate chain

```text
research
  -> provenance/license
  -> candidate
  -> structural validation
  -> disposable sandbox
  -> original-error replay
  -> full regression
  -> protected regression / anti-forgetting
  -> offline staging
  -> real Windows
  -> real NosTale
  -> explicit confirmation
  -> main
```

A missing gate is `NOT_RUN`, not PASS. Simulation PASS is never equivalent to real-runtime PASS.

## Promotion Firewall

Required gates are:

- unit tests
- integration tests
- simulation replay
- protected regression
- static analysis
- provenance
- real Windows
- real NosTale
- explicit human confirmation

The firewall only returns `READY_FOR_PROMOTION` when all required gates are PASS.
It has no production write capability.

## Protected Replay

Protected replay cases represent capabilities that must not regress. A candidate can improve a new scenario and still be rejected if it decreases a protected score beyond the configured tolerance.

Replay cases are append-only evidence records with deterministic fingerprints.

## Sandbox

The current default remains a refusal/no-op backend. A real backend must be explicitly injected and must document its isolation boundary. Core simulation requests reject network access, unsafe paths, invalid timeouts and missing commands.

The sandbox must remain disposable. Candidate source is copied into an isolated workspace; it is never applied directly to the production tree.

## Registry

Models, policies, strategies and knowledge snapshots are registered with parent/version/source commit/run/replay/environment/metrics/validation/provenance/rollback metadata.

Registry state is metadata; promotion remains controlled by the firewall.

## Release rule

Nothing in this P0 block authorizes automatic promotion. The only path to `main` remains validation followed by explicit confirmation, consistent with `docs/BRANCHING_AND_RELEASE_POLICY.md`.
