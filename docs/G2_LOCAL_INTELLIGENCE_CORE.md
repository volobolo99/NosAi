# G2 — Local Intelligence Core

## Scope

G2 starts from the immutable G1 checkpoint and introduces the first offline intelligence boundary: a provider-neutral decision adapter backed by an optional local llama.cpp HTTP server.

## Safety boundary

- The adapter only returns a typed `Decision`.
- It never executes `CandidateAction`.
- Invalid provider output fails closed as `REJECTED`.
- The package has no mandatory inference dependency.
- Internet is not required by the adapter.
- A local llama.cpp server is configured explicitly with `NOSAI_LLAMA_CPP_URL`.

## Configuration

- `NOSAI_LLAMA_CPP_URL` — default `http://127.0.0.1:8080`
- `NOSAI_LLAMA_CPP_MODEL` — default `local`
- `NOSAI_LLAMA_CPP_TIMEOUT` — default `15` seconds
- `NOSAI_LLAMA_CPP_MAX_TOKENS` — default `512`
- `NOSAI_LLAMA_CPP_TEMPERATURE` — default `0`

The endpoint expected by the adapter is the OpenAI-compatible llama.cpp route `/v1/chat/completions`.

## Contract

The model is instructed to return JSON containing `status`, `rationale`, `confidence`, and an optional `action` with `action_id`, `action_type`, `parameters`, and `risk`.

The result is mapped into the canonical G1 `Decision`, `CandidateAction`, and `Risk` contracts. This keeps the model provider replaceable and keeps execution outside the intelligence layer.

## Validation

The unit tests cover structured proposal mapping, fail-closed behavior for invalid output, and dependency-free configuration construction. Real local-model validation belongs to a later G2 host/inference gate and must not be reported as passed until exercised against a real supported local runtime.
