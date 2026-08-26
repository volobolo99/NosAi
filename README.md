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

## Hybrid AI runtime

NosAi now has a provider-neutral AI boundary and a local-first hybrid orchestrator. `HybridOrchestrator` produces normalized decisions but does not execute game actions.

Routing policy:

1. High-confidence decisions stay local for low latency.
2. Low-confidence or explicitly strategic decisions can use OpenAI.
3. OpenAI failures automatically fall back to the local provider.
4. Provider, confidence, latency, fallback state, rationale, and errors are exposed for evaluation/logging.
5. The OpenAI provider uses the Responses API and reads `OPENAI_API_KEY` from the runtime environment.

The default strategic model is configurable with `NOSAI_OPENAI_MODEL` and currently defaults to `gpt-5.6-luna`.

Example wiring:

```python
from app.ai.hybrid import HybridOrchestrator
from app.ai.providers import LocalAIProvider, OpenAIProvider

local = LocalAIProvider(local_decision_function)
openai = OpenAIProvider()
orchestrator = HybridOrchestrator(local, openai, confidence_threshold=0.70)

# Real-time path: normally remains local.
decision = orchestrator.decide(state, objective)

# Strategic path: explicitly permits OpenAI reasoning.
strategic = orchestrator.decide(state, objective, strategic=True)
```

The API key must never be committed to the repository or emitted in logs.

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

The required generic adapter contract remains in `app/client/adapter.py`; the repository does not ship a fake live-client adapter.

## Development principles

1. Preserve runtime behavior during structural work.
2. Make changes in small, reviewable commits/PRs.
3. Run the complete regression suite after structural changes.
4. Measure performance before optimizing it.
5. Do not delete historical documentation or implementation evidence without proving it is redundant.
6. Keep repository configuration single-sourced and reproducible.

## Current roadmap

1. Repository foundation and quality gates. **Complete.**
2. Source quality and architecture audit. **In progress.**
3. Establish the strict live-client adapter and integration contract. **In progress.**
4. Validate real-client observation and visual/game-state perception. **Next.**
5. Connect the hybrid AI orchestrator to the perception/state pipeline.
6. Add a separately gated action transport only after observation is proven.
7. Establish benchmark and regression baselines.
8. Optimize measured bottlenecks.
9. Release hardening.
