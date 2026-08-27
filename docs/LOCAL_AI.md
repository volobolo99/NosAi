# Local AI strategy

NosAi uses a provider-neutral `AIGateway`. The default development provider is Ollama with `qwen3:4b`, selected as a conservative baseline before hardware benchmarking.

## Why
- no per-request API cost;
- local inference and offline operation after model download;
- OpenAI remains an optional cloud provider;
- deterministic fallback remains available.

## Model selection
`NOSAI_LOCAL_MODEL` can override the default model. Future hardware benchmarking should compare 4B, 8B and 14B by startup success, tokens/sec, latency and memory use. Do not select a larger model solely because it is available.

## Safety
Free-form local model output is not converted directly into a game action. It remains proposal-only until parsed into a typed decision and accepted by the deterministic planner and Safety Gate.
