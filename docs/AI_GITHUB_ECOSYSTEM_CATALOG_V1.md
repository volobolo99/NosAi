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
| `openai/openai-agents-python` | multi-agent orchestration, tools, handoffs, tracing | active, widely adopted Python project | MIT | **ADOPT PATTERNS** for agent orchestration, tool contracts, tracing and handoffs; do not replace NosAi brain wholesale |
| `langchain-ai/langgraph` | durable/stateful agent graphs, multi-agent workflows, RAG | active, widely adopted Python project | MIT | **ADOPT PATTERNS** for explicit state graphs, checkpoints, durable execution and controlled branching |
| `DLR-RM/stable-baselines3` | production-oriented RL algorithms | active, documented Python/PyTorch project | MIT | **ADOPT** as optional RL implementation/reference layer for PPO/SAC/TD3 etc.; integrate behind NosAi RL interface |
| `Stable-Baselines-Team/stable-baselines3-contrib` | experimental RL algorithms | active releases, Python, MaskablePPO/RecurrentPPO/TQC/TRPO etc. | MIT | **SELECTIVELY ADOPT** algorithms useful to action masking/recurrent policy; keep experimental modules isolated |
| `vwxyzjn/cleanrl` | research-friendly RL implementations | large, research-oriented Python/PyTorch project | NOASSERTION / project-specific | **REFERENCE ONLY** until license compatibility is explicitly cleared; excellent algorithm clarity, not a direct dependency |
| `confident-ai/deepeval` | LLM/agent evaluation | active Python evaluation project | Apache-2.0 | **ADOPT PATTERNS** for AI evaluation suites, metrics and regression evaluation; keep NosAi report schema authoritative |
| `mlflow/mlflow` | experiment tracking, evaluation, tracing, model lifecycle | active, large OSS AI engineering platform, extensive releases | Apache-2.0 | **ADOPT PATTERNS / CANDIDATE** for experiment lineage, model/version registry and evaluation correlation; do not replace NosAi Test Center without a focused benchmark |
| `qdrant/qdrant` | vector search / memory / retrieval | production-oriented vector DB, Rust, REST/gRPC, hybrid search | Apache-2.0 | **CANDIDATE** for long-term semantic memory/retrieval; do not add dependency until benchmarked against current memory implementation |
| `qdrant/qdrant-client` | Python vector DB client | typed sync/async client, API coverage | Apache-2.0 | **CANDIDATE** paired with Qdrant if selected |
| `ggml-org/llama.cpp` | local CPU/GPU LLM inference | active, local inference and API server, broad hardware support | MIT | **CANDIDATE / HIGH PRIORITY** for local/offline inference and fallback model runtime |
| `vllm-project/vllm` | high-throughput LLM serving | large active project, many contributors/releases | Apache-2.0 | **OPTIONAL SERVER PATH** for GPU/cloud inference; not the default Windows runtime |
| `OpenRL-Lab/openrl` | unified RL / multi-agent / self-play / offline RL | modular RL framework | Apache-2.0 | **REFERENCE / SELECTIVE ADOPTION**; evaluate before introducing overlapping abstractions |
| `ContinualAI/avalanche` | continual learning, replay, benchmarks, evaluation | active OSS PyTorch library with benchmarks, strategies, metrics and reproducibility focus | MIT | **ADOPT PATTERNS / CANDIDATE** for the Evolution Lab's continual-learning benchmark and anti-forgetting layer; prefer narrow adapters over importing the whole framework |
| `ContinualAI/continual-learning-baselines` | reproducible continual-learning baselines | benchmark repository with reproduced strategies and reference results | check upstream before dependency use | **REFERENCE** for anti-forgetting experiments and baseline comparisons |
| `online-ml/river` | streaming/online ML, drift detection, incremental learning | active Python project with incremental APIs, drift detectors and progressive validation | BSD-3-Clause | **ADOPT PATTERNS / CANDIDATE** for lightweight online adaptation and concept-drift detection; keep gameplay policy updates behind promotion gates |
| `open-telemetry/opentelemetry-python` | traces, metrics, telemetry | stable traces/metrics, active OSS project | Apache-2.0 | **ADOPT** as observability standard where compatible; use semantic correlation instead of inventing a second telemetry model |
| `treeverse/dvc` | data/model/experiment versioning and reproducible pipelines | mature OSS project for reproducible ML workflows | Apache-2.0 | **CANDIDATE** for large training datasets, model artifacts and reproducible evolution runs; do not duplicate Git for ordinary source code |
| `arunponnusamy/object-detection-opencv` | YOLO/OpenCV example | runnable example | MIT | **REFERENCE ONLY**; use established CV stack rather than importing example code |
| `jacobgil/pytorch-grad-cam` | model explainability/CAM | established PyTorch explainability library | MIT | **OPTIONAL** for AI diagnostics/visual explanations, not core runtime |

## Architecture decision after the continual-growth review

NosAi is now explicitly designed as an **offline-first, online-assisted continual-improvement system**.

The local gameplay core remains authoritative and must continue to operate without Internet access. Online services feed a separate Evolution Lab that researches, validates and experiments with new knowledge, strategies, models and code. Nothing moves directly from the Internet into the offline core.

The lifecycle is:

`observe -> collect -> fingerprint -> research -> candidate -> simulate -> compare -> compose -> validate -> promote-to-staging -> offline regression -> real-Windows retest -> real-NosTale retest -> consolidate`

### New architectural safeguards

1. **Knowledge maturity states**: `candidate -> experimental -> validated -> consolidated`.
2. **Model/strategy registry**: every learned policy, local model, strategy package and knowledge snapshot has a version, provenance, parent, metrics and rollback reference.
3. **Anti-forgetting gate**: new learning must be evaluated against a fixed regression/replay set before consolidation. A higher score on new scenarios is not enough if old capabilities regress.
4. **Drift detection**: streaming observations may trigger investigation, but they cannot silently rewrite the production policy.
5. **Reproducible evolution runs**: code commit, model version, dataset/replay snapshot, parameters, environment profile and evidence IDs are linked.
6. **Unified observability**: use a stable NosAi correlation chain compatible with OpenTelemetry concepts: `run_id -> agent_id -> scenario_id -> state_id -> tool_call_id -> model_call_id -> evidence_id -> test_result_id`.
7. **Offline survivability**: the runtime must have a capability matrix and explicit fallback behavior. Online-only capabilities are never treated as required for gameplay.
8. **Promotion firewall**: simulation success creates evidence, not an automatic production update.

## Immediate architecture improvements selected for NosAi

### 1. Agent orchestration

Use ideas from OpenAI Agents SDK and LangGraph to formalize explicit agent roles, typed tool contracts, state transitions, handoffs, bounded loops, checkpoints, trace IDs, cancellation/timeouts and deterministic replay where possible. NosAi's executive controller remains authoritative.

### 2. AI evaluation

Use DeepEval/MLflow-style evaluation concepts to expand the existing AI Lab into scenario datasets, deterministic regression cases, trajectory evaluation, tool-call correctness, planning quality, memory/retrieval quality, constraint adherence and baseline-vs-candidate comparisons. NosAi's report schema remains authoritative.

### 3. Continual learning

Use Avalanche as a reference for benchmark/stream/replay structure and continual-learning metrics, and River as a reference for lightweight streaming adaptation and concept-drift detection. Do not permit online learning to mutate the production policy without passing the anti-forgetting and promotion gates.

### 4. Reinforcement learning

Keep RL behind a stable NosAi interface. Stable-Baselines3 is the preferred external reference/dependency candidate. Use SB3-Contrib only for algorithms that directly add value, especially action masking or recurrent policies.

### 5. Memory / retrieval

Evaluate Qdrant as a future semantic-memory backend. The existing NosAi memory model remains the source of truth until benchmarks show measurable improvement in retrieval quality, latency, resource use and operational complexity.

### 6. Local inference

Keep llama.cpp as the primary candidate for local/offline inference. Keep vLLM as the high-throughput GPU/server option. The runtime must select inference providers through an interface rather than binding the AI architecture to one serving engine.

### 7. Reproducibility and artifact lineage

Evaluate DVC for large datasets, model artifacts and evolution experiments that do not fit comfortably in Git. Git remains authoritative for source code and configuration; DVC is only considered where artifact scale/reproducibility justifies it.

### 8. Observability

Adopt OpenTelemetry-compatible tracing/metrics semantics. Every AI operation should be correlatable through the NosAi chain above so a failed real NosTale scenario can be reproduced in simulation and compared against candidate implementations.

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

**P0:** offline-first evolution architecture, promotion firewall, replay/regression anti-forgetting, unified provenance/observability, AI evaluation, RL adapter boundary.

**P1:** continual-learning benchmark harness, semantic memory benchmark with Qdrant, local inference abstraction, reproducible artifact lineage.

**P2:** optional vLLM server path, explainability tooling, experimental RL algorithms.

## Validation gate

Nothing from this catalog is promoted to `main` directly. Any adoption follows:

`research -> license/provenance -> isolated prototype -> unit/integration tests -> CI -> simulation -> anti-forgetting regression -> real Windows test -> real NosTale test -> regression -> human confirmation -> main`.
