# NosAi

NosAi is the full-runtime fusion project currently at version **4.21.0**.

## Repository status

The repository is source-first: the runtime lives in `app/`, tests live in `tests/`, and CI validates the source tree directly. Runtime behavior is protected by regression tests while the architecture and source quality are audited.

## Branching and release model

- `main` is the **confirmed/stable baseline only**. It represents the latest version explicitly promoted after validation.
- `develop/nosai-next` is the **active integration and validation branch**. New NosAi work, fixes, experiments, and test iterations are developed here.
- A version is promoted to `main` only after the validation gate is satisfied and the version is explicitly confirmed for release.
- Release promotion is performed through a pull request from `develop/nosai-next` to `main`; direct development on `main` is not part of the normal workflow.
- Historical/feature branches remain available for traceability and focused work, but `develop/nosai-next` is the integration baseline for the next candidate release.

The authoritative workflow is documented in `docs/BRANCHING_AND_RELEASE_POLICY.md`.

## Version metadata

`pyproject.toml` is the package/build source of truth and currently declares **4.21.0**. `version.json` and the README release metadata are kept aligned with it. A version mismatch is a release-blocking defect and must be corrected before promotion.

## Baseline

- Version: `4.21.0`
- Release: `full-runtime-fusion-hardened`
- Python: `>=3.10`
- Runtime package: `app/`
- Test suite: `tests/`
- Build/configuration source of truth: `pyproject.toml`

## NosTale strategy model

The repository contains an explicit source-grounded NosTale strategy layer in `app/nostale/strategy.py`, based on the attached strategy document. It turns proposed state variables and strategic rules into inspectable inputs for planning and reward shaping instead of burying assumptions inside a neural policy.

## Live-client pre-flight

NosAi never guesses how to attach to the game client. A real integration must provide an explicit `ClientAdapter` implementation and configure it as `module:attribute` through `NOSAI_CLIENT_ADAPTER` or `--client-adapter`.

Before live runtime is allowed, the pre-flight performs Python/dependency, runtime import, client connection, normalized state-read and non-destructive action-validation checks. A failed live check returns exit code `1` with stable check ID, phase, expected/actual values and exception information.

## Real NosTale observation adapter

`WindowsNosTaleAdapter` is the concrete boundary for a real Windows NosTale client. It detects only configured process names and requires a visible client window. It is observation-only while visual/game-state perception is being validated.

## Development principles

1. Preserve runtime behavior during structural work.
2. Make changes reviewable and traceable.
3. Run the complete regression suite after structural changes.
4. Measure performance before optimizing it.
5. Keep repository configuration reproducible.
6. Treat source-derived gameplay mechanics as hypotheses until validated.
7. Never promote an unvalidated candidate into `main`.
8. Keep the gameplay core offline-first: Internet may improve NosAi, but must never be required for basic gameplay.
9. Never consolidate learned knowledge, models or strategies without anti-forgetting regression, provenance and rollback information.
10. Never report a sandbox candidate as PASS when the real OS-level sandbox or required runtime payload was not actually available.

## Current architecture direction

NosAi is formally **offline-first and continually improving**. Online services feed an isolated Evolution Lab rather than directly controlling gameplay:

`real experience -> observation -> online research -> candidate -> sandbox -> replay -> regression -> anti-forgetting -> offline staging -> real Windows -> real NosTale -> explicit confirmation -> consolidation`

The P0 block now contains the promotion/evidence contracts, protected replay execution, candidate regression evaluation and a real Windows Sandbox CLI backend. The OS-level backend deliberately fails closed until it is exercised on a supported Windows host with an immutable runtime payload.

See:

- `docs/NOSAI_OFFLINE_FIRST_EVOLUTION_ARCHITECTURE_V2.md`
- `docs/NOSAI_MASTER_ROADMAP_V3.md`
- `docs/P0_EVOLUTION_GATES.md`
- `docs/WINDOWS_SANDBOX_REPLAY_REGRESSION.md`
- `docs/AI_GITHUB_ECOSYSTEM_CATALOG_V1.md`

## Current roadmap

| Area | Maturity |
|---|---:|
| Repository/release structure | 95% |
| Test/evidence foundation | 80% |
| Research -> candidate -> simulation | 70% |
| Promotion/evolution governance | 70% |
| Protected replay | 70% |
| Candidate regression | 45% |
| Windows Sandbox backend | 35% (host validation pending) |
| Offline-first AI core | 55% |
| RL layer | 45% |
| Memory/retrieval | 40% |
| Local inference | 30% |
| Continual learning / anti-forgetting | 65% (gate; training loop pending) |
| Unified observability | 45% |
| Model/strategy registry | 60% (contract + local store) |
| Real Windows runtime | 25% |
| Real NosTale client | 15% |
| Real action transport | 5% (intentionally gated) |
| Autonomous evolution loop | 25% |

These are engineering maturity estimates, not claims that real-world tests have passed.