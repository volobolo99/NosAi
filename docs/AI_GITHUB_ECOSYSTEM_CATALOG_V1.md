# NosAi — GitHub AI Ecosystem Catalog V1

Date: 2026-08-27
Branch: `develop/nosai-next`

## Purpose

Catalog of mature, active, open-source AI projects reviewed as architectural references for NosAi. This is **not** a certification list. A repository being popular, active, or widely used does not prove that every release is correct for NosAi. Every candidate must still pass NosAi's own dependency, license, security, compatibility, CI, simulation, and real-Windows validation gates.

## Selection criteria

Repositories are considered high-signal when several of these are present: active maintenance, public releases/tags, substantial adoption, documented APIs, tests/CI, explicit license, reproducible installation, established maintainers, and a clear architectural fit.

## Catalog

| Project | Area | Signal observed | License | NosAi decision |
|---|---|---|---|---|
| `openai/openai-agents-python` | multi-agent orchestration, tools, handoffs, tracing | active, 28k+ stars, 4.6k+ forks, Python, releases/issues | MIT | **ADOPT PATTERNS** for agent orchestration, tool contracts, tracing and handoffs; do not replace NosAi brain wholesale |
| `langchain-ai/langgraph` | durable/stateful agent graphs, multi-agent workflows, RAG | active, 40k+ stars, 6.8k+ forks, Python, MIT | MIT | **ADOPT PATTERNS** for explicit state graphs, checkpoints, durable execution and controlled branching |
| `DLR-RM/stable-baselines3` | production-oriented RL algorithms | active, 13k+ stars, 2k+ forks, Python/PyTorch, documented releases | MIT | **ADOPT** as optional RL implementation/reference layer for PPO/SAC/TD3 etc.; integrate behind NosAi RL interface |
| `Stable-Baselines-Team/stable-baselines3-contrib` | experimental RL algorithms | active releases, Python, MaskablePPO/RecurrentPPO/TQC/TRPO etc. | MIT | **SELECTIVELY ADOPT** algorithms useful to action masking/recurrent policy; keep experimental modules isolated |
| `vwxyzjn/cleanrl` | research-friendly RL implementations | 10k+ stars, 1k+ forks, Python/PyTorch | NOASSERTION / project-specific | **REFERENCE ONLY** until license compatibility is explicitly cleared; excellent algorithm clarity, not a direct dependency |
| `confident-ai/deepeval` | LLM/agent evaluation | active, 17k+ stars, 1.8k+ forks, Python | Apache-2.0 | **ADOPT PATTERNS** for AI evaluation suites, metrics and regression evaluation; keep NosAi report schema authoritative |
| `qdrant/qdrant` | vector search / memory / retrieval | production-oriented vector DB, Rust, REST/gRPC, hybrid search | Apache-2.0 | **CANDIDATE** for long-term semantic memory/retrieval; do not add dependency until benchmarked against current memory implementation |
| `qdrant/qdrant-client` | Python vector DB client | typed sync/async client, API coverage | Apache-2.0 | **CANDIDATE** paired with Qdrant if selected |
| `vllm-project/vllm` | high-throughput LLM serving | large active project, 80k+ stars, many contributors/releases | Apache-2.0 | **OPTIONAL SERVER PATH** for GPU/cloud inference; not the default Windows runtime |
| `ggml-org/llama.cpp` | local CPU/GPU LLM inference | active, OpenAI-compatible local server/API, broad hardware support | MIT | **CANDIDATE** for local/offline inference and fallback model runtime |
| `OpenRL-Lab/openrl` | unified RL / multi-agent / self-play / offline RL | modular RL framework | Apache-2.0 | **REFERENCE / SELECTIVE ADOPTION**; evaluate before introducing overlapping abstractions |
| `langchain-ai/langchain` | LLM application integrations/RAG/tooling | very large ecosystem | MIT | **REFERENCE ONLY**; avoid adding broad dependency where narrower components are preferable |
| `arunponnusamy/object-detection-opencv` | YOLO/OpenCV example | MIT, runnable example | MIT | **REFERENCE ONLY**; use established CV stack rather than importing example code |
| `jacobgil/pytorch-grad-cam` | model explainability/CAM | established PyTorch explainability library | MIT | **OPTIONAL** for AI diagnostics/visual explanations, not core runtime |

## What remains in the catalog

The catalog intentionally retains projects that may become useful later. Retaining a project does **not** mean installing it. Each entry has a role: adopt, candidate, reference, or reject.

## Immediate architecture improvements selected for NosAi

### 1. Agent orchestration

Use ideas from OpenAI Agents SDK and LangGraph to formalize:

- explicit agent roles;
- typed tool contracts;
- state transitions;
- handoffs;
- bounded loops;
- checkpoints;
- trace IDs;
- cancellation/timeouts;
- deterministic replay where possible.

NosAi's existing executive controller remains authoritative.

### 2. AI evaluation

Use DeepEval-style evaluation concepts to expand the existing AI Lab into:

- scenario datasets;
- deterministic regression cases;
- model/agent quality metrics;
- trajectory evaluation;
- tool-call correctness;
- planning quality;
- memory/retrieval quality;
- safety/constraint adherence;
- baseline-vs-candidate comparisons.

### 3. Reinforcement learning

Keep RL behind a stable NosAi interface. Stable-Baselines3 is the preferred external reference/dependency candidate because it explicitly describes reliable PyTorch implementations, common interfaces, custom environments/policies, callbacks, type hints and coverage. Use SB3-Contrib only for algorithms that directly add value, especially action masking or recurrent policies.

CleanRL is a research reference only until license requirements are resolved.

### 4. Memory / retrieval

Evaluate Qdrant as a future semantic-memory backend. The existing NosAi memory model remains the source of truth until benchmarks show a measurable improvement in retrieval quality, latency, resource use and operational complexity.

### 5. Local inference

Keep `llama.cpp` as the primary candidate for a local/offline inference path. Keep vLLM as the high-throughput GPU/server option. The runtime must select inference providers through an interface rather than binding the AI architecture to one serving engine.

### 6. Observability and evaluation correlation

Every AI operation should be correlatable through:

`run_id -> agent_id -> scenario_id -> state_id -> tool_call_id -> model_call_id -> evidence_id -> test_result_id`

This is required so a failed real NosTale scenario can be reproduced in simulation and compared against candidate implementations.

## Explicitly rejected strategy

Do **not** merge entire frameworks into NosAi simply because they are popular. Do not duplicate functionality already present in NosAi. Prefer extracting a proven architectural pattern, wrapping a mature library behind a narrow adapter, or reimplementing a small well-understood component when that produces a smaller and more maintainable dependency surface.

## License and provenance rule

Before any external code becomes a dependency or is copied into NosAi, record:

1. repository URL;
2. commit/tag/version;
3. license and compatibility;
4. exact component used;
5. security review status;
6. compatibility test status;
7. reason for adoption;
8. replacement/rollback path.

No external code is considered trusted solely because it is hosted on GitHub.

## Current priority

**P0:** orchestration/state graph patterns, AI evaluation, RL adapter boundary, research provenance.

**P1:** semantic memory benchmark with Qdrant, local inference abstraction, richer trajectory evaluation.

**P2:** optional vLLM server path, explainability tooling, experimental RL algorithms.

## Validation gate

Nothing from this catalog is promoted to `main` directly. Any adoption follows:

`research -> license/provenance -> isolated prototype -> unit/integration tests -> CI -> simulation -> real Windows test -> real NosTale test -> regression -> human confirmation -> main`.
