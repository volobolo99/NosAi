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

The repository now contains an explicit source-grounded NosTale strategy layer in `app/nostale/strategy.py`, based on the attached `Guida Strategica e Analisi NosTale.pdf`. It turns the document's proposed state variables and strategic rules into inspectable inputs for planning and reward shaping instead of burying assumptions inside a neural policy.

The model currently exposes:

- HP/MP ratios, Dignity, grade differential and elemental/resistance signals.
- Target distance/type and Time-Space room objectives.
- Hardcore raid life-pool and contribution state.
- A 100% elemental-resistance threshold signal and a `-400` Dignity guard.
- Explicit strategy modes for kill-all, survival, target elimination, switch access and escort rooms.
- Reward metadata containing source provenance for later validation.

See `docs/NOSTALE_STRATEGY_MODEL.md` for the source-to-runtime mapping and validation policy. The PDF is treated as a source-derived engineering hypothesis until individual mechanics are verified against live observations or authoritative references.

## Live-client pre-flight

NosAi never guesses how to attach to the game client. A real integration must provide an explicit `ClientAdapter` implementation and configure it as `module:attribute` through `NOSAI_CLIENT_ADAPTER` or `--client-adapter`.

Before live runtime is allowed, the pre-flight performs:

1. Python and dependency checks.
2. Runtime module import checks.
3. Client connection check.
4. Normalized client-state read check.
5. Non-destructive action-validation check (no game action is executed).

A failed live check returns exit code `1` and reports a stable check ID, phase, expected value, actual value, exception type, and exception text. The live probe is deliberately non-destructive.

## Real NosTale observation adapter

`WindowsNosTaleAdapter` is the first concrete boundary for a real Windows NosTale client. It detects only configured process names (`NostaleClientX.exe` and `NostaleClient.exe` by default), requires a visible client window, and returns normalized PID/window geometry metadata.

The adapter is intentionally **observation-only**. It does not inject keyboard/mouse input, patch memory, open a game-action transport, or execute a game action. This is a hard safety boundary while visual/game-state perception is validated.

## Development principles

1. Preserve runtime behavior during structural work.
2. Make changes in small, reviewable commits/PRs.
3. Run the complete regression suite after structural changes.
4. Measure performance before optimizing it.
5. Do not delete historical documentation or implementation evidence without proving it is redundant.
6. Keep repository configuration single-sourced and reproducible.
7. Treat source-derived gameplay mechanics as hypotheses until validated by observations.
8. Never promote an unvalidated candidate into `main`.
9. Keep the gameplay core offline-first: Internet may improve NosAi, but must never be required for basic gameplay.
10. Never consolidate learned knowledge, models or strategies without anti-forgetting regression, provenance and rollback information.

## Current architecture direction

NosAi is now formally **offline-first and continually improving**:

`real experience -> observation -> online research (when available) -> candidate -> simulation/replay -> evaluation -> anti-forgetting -> offline staging -> real Windows -> real NosTale -> consolidation -> new offline baseline`

Online services are an Evolution Lab, not a direct source of gameplay behavior. Knowledge moves through explicit maturity states (`candidate -> experimental -> validated -> consolidated`) and the Promotion Firewall prevents simulation or online research from directly changing the production core.

See:

- `docs/NOSAI_OFFLINE_FIRST_EVOLUTION_ARCHITECTURE_V2.md`
- `docs/NOSAI_MASTER_ROADMAP_V2.md`
- `docs/AI_GITHUB_ECOSYSTEM_CATALOG_V1.md`

## Current roadmap

1. Repository/release foundation. **95%**
2. Test/evidence foundation. **80%**
3. Research → candidate → simulation pipeline. **70%**
4. Offline-first AI core implementation. **55%**
5. Local inference abstraction + llama.cpp benchmark. **30%**
6. RL adapter and offline training/evaluation. **45%**
7. Continual learning + anti-forgetting. **25%**
8. Memory/retrieval benchmark. **40%**
9. Model/strategy registry. **20%**
10. Unified observability. **45%**
11. Real Windows runtime validation. **25%**
12. Real NosTale perception/validation. **15%**
13. Action transport. **5%** (intentionally gated)
14. Autonomous evolution loop. **20%**

These are engineering maturity estimates, not claims that real-world tests have passed.
