# NosAi

NosAi is the full-runtime fusion project currently at confirmed version **4.19.2**.

## Repository status

The repository is source-first: the runtime lives in `app/`, tests live in `tests/`, and CI validates the source tree directly. Runtime behavior is protected by regression tests while the architecture and source quality are audited.

## Confirmed baseline

- Branch: `main`
- Confirmed version: `4.19.2`
- Release: `full-runtime-fusion-hardened`
- Python: `>=3.10`
- Runtime package: `app/`
- Test suite: `tests/`
- Build/configuration source of truth: `pyproject.toml`

`main` is the confirmed/stable baseline only. New development and candidate releases are worked on in `develop/nosai-next` and promoted to `main` only after validation and explicit confirmation.

## Development workflow

See `docs/BRANCHING_AND_RELEASE_POLICY.md` for the candidate lifecycle, validation gate, versioning rule and promotion procedure.

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
