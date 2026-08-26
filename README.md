# NosAi

NosAi is the full-runtime fusion project currently at version **4.19.2**.

## Repository status

The repository is source-first: the runtime lives in `app/`, tests live in `tests/`, and CI validates the source tree directly. Runtime behavior is protected by regression tests while the architecture and source quality are audited.

## Baseline

- Version: `4.19.2`
- Release: `full-runtime-fusion-hardened`
- Python: `>=3.10`
- Runtime package: `app/`
- Test suite: `tests/`
- Build/configuration source of truth: `pyproject.toml`

## Live-client pre-flight

NosAi never guesses how to attach to the game client. A real integration must provide an explicit `ClientAdapter` implementation and configure it as `module:attribute` through `NOSAI_CLIENT_ADAPTER` or `--client-adapter`.

Before live runtime is allowed, the pre-flight performs:

1. Python and dependency checks.
2. Runtime module import checks.
3. Client connection check.
4. Normalized client-state read check.
5. Non-destructive action-validation check (no game action is executed).

A failed live check returns exit code `1` and reports a stable check ID, phase, expected value, actual value, exception type, and exception text. The live probe is deliberately non-destructive.

Example:

```text
set NOSAI_CLIENT_ADAPTER=my_adapter:adapter
nosai-preflight --require-client
```

For machine-readable diagnostics:

```text
nosai-preflight --require-client --json
```

## Real NosTale observation adapter

`WindowsNosTaleAdapter` is the first concrete boundary for a real Windows NosTale client. It detects only configured process names (`NostaleClientX.exe` and `NostaleClient.exe` by default), requires a visible client window, and returns normalized PID/window geometry metadata.

The adapter is intentionally **observation-only**. It does not inject keyboard/mouse input, patch memory, open a game-action transport, or execute a game action. This is a hard safety boundary while visual/game-state perception is validated.

Local probe:

```text
nosai-client-probe
nosai-client-probe --json
```

A non-zero exit means the client could not be observed successfully; it does not mean NosAi attempted to control the game. Custom process names can be supplied with:

```text
set NOSAI_NOSTALE_PROCESS_NAMES=NostaleClientX.exe;NostaleClient.exe
```

## Local NosTale asset scanner

NosAi can inspect the **user's own local NosTale data directory** without downloading or modifying game assets. The scanner identifies the asset families required by the planned avatar/effect renderer, records file size and SHA-256, and can optionally invoke an installed `taletool` binary for format-aware classification.

The scanner intentionally keeps proprietary client assets outside the repository. It records paths and metadata only; extraction/caching belongs to a later, separately tested stage.

Example:

```text
nosai-assets-scan "C:\GameforgeLive\Nostale\NostaleData"
```

If `taletool` is installed on `PATH`, its JSON scan is included automatically. A custom executable can be supplied with `--taletool`.

The scanner currently maps the renderer-critical families including player sprites (`NSppData`), player animations (`NSpcData`), player resource remaps (`NSpmData`), player index (`NSpnData`), effect definitions/animation/geometry/texture families, and monster/NPC resources.

The format model is based on Taletool's documented NosTale structures: `NSpcData` supplies ordered player sprite animation frames, `NSpmData` remaps the eight player rendering resource slots, and `NSpnData` links player entries to animation/remap/resource keys.

## Development principles

1. Preserve runtime behavior during structural work.
2. Make changes in small, reviewable commits/PRs.
3. Run the complete regression suite after structural changes.
4. Measure performance before optimizing it.
5. Do not delete historical documentation or implementation evidence without proving it is redundant.
6. Keep repository configuration single-sourced and reproducible.
7. Never commit proprietary NosTale client archives or extracted assets.

## Current roadmap

1. Repository foundation and quality gates. **Complete.**
2. Source quality and architecture audit. **In progress.**
3. Establish the strict live-client adapter and integration contract. **In progress.**
4. Validate real-client observation and visual/game-state perception. **Next.**
5. Discover and index local NosTale assets for the avatar/effect renderer. **Started.**
6. Build the local 2.5D avatar/effect renderer and replay layer.
7. Add a separately gated action transport only after observation is proven.
8. Establish benchmark and regression baselines.
9. Optimize measured bottlenecks.
10. Release hardening.
