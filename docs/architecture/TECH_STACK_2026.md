# NosAi Technology Stack 2026

## Purpose

This document defines the infrastructure and AI-tooling strategy for NosAi. The goal is to reuse mature components where they are commodity capabilities and reserve NosAi-specific engineering for orchestration, repository intelligence, memory, evaluation, verification, and policy.

## Architecture principles

1. The NosAi core remains provider-neutral.
2. Deterministic runtime safety stays local and authoritative.
3. Agents never receive unrestricted host access.
4. Every generated change is tested and independently evaluated before promotion.
5. Observability is a first-class data source for evaluation and learning.
6. External services are adapters, not hard dependencies of the domain model.
7. New infrastructure is introduced only after a measurable need or benchmark.

## Adopt now

| Capability | Technology | Role |
|---|---|---|
| Source control | GitHub | Code, issues, PRs, releases |
| CI | GitHub Actions | lint, tests, evaluation and artifacts |
| Packaging | Python + pyproject.toml | Single source of package configuration |
| Execution isolation | Docker | Agent/test sandbox |
| Database | PostgreSQL | Durable relational state |
| Vector search | pgvector | Initial semantic memory |
| Private network | Tailscale | Secure node-to-node connectivity |
| Telemetry | OpenTelemetry | Vendor-neutral traces/metrics |
| AI observability | Langfuse | LLM/agent traces, prompts and evaluation data |
| Error monitoring | Sentry | Application errors and performance |
| Infrastructure monitoring | Grafana stack | Metrics/log dashboards |

## Evaluate behind adapters

- LangGraph: stateful agent/workflow orchestration.
- OpenHands: autonomous coding-agent executor.
- OpenCode/Cline: alternative coding-agent executors.
- Phoenix: LLM/agent evaluation and tracing.
- Ragas: RAG/evaluation metrics.
- Qdrant: alternative vector database if pgvector becomes insufficient.
- Redis: queue/cache when concurrent workers require it.
- LiteLLM: model gateway if multi-provider routing becomes necessary.
- S3-compatible object storage: large artifacts, datasets and reports.
- Coolify: deployment control plane if it simplifies VPS operations.

## NosAi-owned components

### 1. Control Plane

Owns task lifecycle, policies, agent selection, budgets, approvals and promotion decisions.

### 2. Repository Intelligence Engine

Builds a compact task-specific context from repository files, symbols, tests, history and previous solutions before invoking a coding agent.

### 3. Knowledge Engine

Stores episodic, semantic, procedural, repository and evaluation memory. Initial persistence uses PostgreSQL + pgvector.

### 4. Evaluation Engine

Combines deterministic tests, regression tests, benchmarks, static checks, security checks and optional model-based evaluators.

### 5. Verification Engine

Independently checks whether a proposed patch actually addresses the stated task and whether it introduces regressions.

### 6. Sandbox Manager

Creates isolated Git worktrees/containers, applies resource limits, executes agents and tests, captures artifacts, and destroys temporary environments.

### 7. Lesson Engine

Converts verified outcomes into durable knowledge. Failed attempts are retained as negative evidence rather than silently discarded.

## Initial deployment target

Start with one European VPS (Hetzner Cloud is the preferred candidate), Docker, PostgreSQL/pgvector and Tailscale. Do not purchase dedicated hardware until measured workload requires it.

The local Windows development machine remains the primary development and AI-compute node. The VPS provides durable services, APIs, databases, telemetry, backups and orchestration support.

## Promotion pipeline

```text
Task
  -> Repository Intelligence
  -> Agent Selection
  -> Isolated Worktree/Sandbox
  -> Agent Execution
  -> Patch
  -> Deterministic Tests
  -> Independent Verification
  -> Regression/Evaluation
  -> Policy Gate
  -> Commit/PR
  -> Lesson Extraction
  -> Knowledge Store
```

No step may bypass the policy gate.

## Migration rule

Do not integrate every candidate technology at once. Add one capability at a time, establish a baseline, run a regression/evaluation gate, and retain the component only when it improves a defined metric or materially reduces operational complexity.
