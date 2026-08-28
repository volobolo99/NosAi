# NosAi — llama.cpp Runtime Truth Audit

## Purpose

This document records the repository-grounded state used to decide the next Local LLM bring-up step. It intentionally supersedes assumptions from earlier reports when those reports differ from the checked-in source.

## Verified source of truth

On `develop/nosai-next`, `app/llm/llama_cpp.py` currently defines:

- Base URL: `http://127.0.0.1:8080`
- Model identifier: `local`
- Timeout: `15.0` seconds
- Max tokens: `512`
- Temperature: `0.0`
- HTTP client: Python standard-library `urllib.request`
- Chat endpoint: `<base_url>/v1/chat/completions`
- Decision output: the provider maps the server response into the shared `Decision` contract.

The provider is proposal-only. It does not execute game actions. Invalid/unavailable responses are converted into a `REJECTED` decision with zero confidence.

## Important discrepancy found

Earlier bring-up reports described a different implementation (for example a `Qwen2.5-7B-Instruct-Q4_K_M.gguf` default, a 2-second timeout, 256 output tokens, and an explicit automatic switch to `RuleBasedDecisionProvider`). Those values are **not the current checked-in values** of `app/llm/llama_cpp.py`.

The current source instead uses the generic model identifier `local`, 15 seconds, 512 tokens and temperature 0.0. Therefore no model name, latency target, or fallback behavior should be declared PASS based only on those earlier reports.

## Contract boundary

The shared contracts define `DecisionProvider.decide(state, goal) -> Decision`, and `Decision` requires a valid status, confidence range, provider and optional action.

The repository also contains a dedicated `nosai/runtime/` package with runtime components including the orchestrator, safety gate, sandbox, adapter, observation and telemetry modules. Therefore the earlier statement that `nosai/runtime/` was absent is not repository-truth.

## Decision for the next gate

The correct next step is **contract-first Local LLM validation**, not immediate performance tuning and not immediate live-client activation.

Order:

1. Keep the model/server external to Git; do not commit binary weights.
2. Validate the checked-in HTTP contract deterministically with mocked transport.
3. Validate rejection behavior when the server is unavailable or malformed.
4. Run CI/Test Center on the new coverage.
5. Only after those gates are green, perform host-side llama.cpp bring-up with the actual model and measure latency/VRAM on the real machine.
6. Treat real host measurements as the source of truth for the final runtime configuration.

## Safety rule

Until the real host endpoint is exercised, Local LLM status remains **UNVERIFIED / host setup pending**. No claim of successful real inference or target latency is made from static source inspection alone.
