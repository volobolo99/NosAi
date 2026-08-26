# Embedding benchmark matrix

## Decision
Use a local-first strategy. The first real candidate is `qwen3-embedding:0.6b` through Ollama because it is small enough for practical local inference while the Qwen3 Embedding family explicitly targets text/code retrieval and multilingual use. Compare it against BGE-M3 and OpenAI `text-embedding-3-small` only on the same corpus.

## Corpus slices

1. repository code and symbols;
2. failures and stack traces;
3. tests and expected behavior;
4. documentation/architecture;
5. verified lessons;
6. Italian/English mixed queries.

## Metrics

- Recall@1/5/10 against a labeled relevant-set oracle;
- Precision@K;
- filtered recall by repository/project;
- median and p95 embedding latency;
- median and p95 retrieval latency;
- vector storage footprint;
- deterministic repeatability;
- failure rate/offline behavior.

## Promotion gate

A model is not selected by a generic leaderboard. It must beat the deterministic baseline and meet the minimum quality threshold on NosAi's own corpus. The chosen model remains an adapter and can be replaced without changing the Knowledge Engine.

## Providers

- `OllamaEmbeddingProvider`: primary local candidate;
- `OpenAIEmbeddingProvider`: cloud reference/fallback;
- additional local models: benchmark-only until measured.

No provider is allowed to decide truth, verification, or promotion.
