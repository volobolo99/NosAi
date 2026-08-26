# NosAi Control Plane

## Goal

The Control Plane is the coordination layer between a task, repository intelligence, agents, sandboxes, verification, evaluation and durable knowledge. It must not own game-client control; the existing client-adapter/action-validation boundary remains authoritative.

## Logical components

```text
Task Intake
   |
   v
Policy / Budget Gate
   |
   v
Repository Intelligence ----> Knowledge Engine
   |
   v
Agent Selector
   |
   v
Sandbox Manager
   |
   v
Agent Executor(s)
   |
   v
Patch / Artifact Store
   |
   +--> Deterministic Tests
   +--> Independent Verification
   +--> Evaluation / Regression
   |
   v
Promotion Gate
   |
   +--> PR / Commit
   +--> Lesson Extraction
   |
   v
Knowledge Engine
```

## Provider-neutral contracts

The core should depend on interfaces equivalent to:

- `TaskSource`
- `RepositoryContextProvider`
- `AgentExecutor`
- `SandboxProvider`
- `TestRunner`
- `Verifier`
- `Evaluator`
- `ArtifactStore`
- `KnowledgeStore`
- `TelemetrySink`
- `PromotionPolicy`

External implementations (OpenHands, OpenAI, LangGraph, Langfuse, Sentry, Qdrant, etc.) must sit behind adapters.

## State model

Every task run should have a durable identifier and explicit states:

`QUEUED -> CONTEXT_READY -> PLANNED -> EXECUTING -> TESTING -> VERIFYING -> EVALUATING -> PROMOTABLE | REJECTED | BLOCKED`

Retries must create explicit attempts rather than overwriting the previous attempt.

## Required run record

At minimum store:

- task ID and source
- repository/ref
- agent/provider/model identifier
- prompt or instruction version
- context manifest
- sandbox identifier
- changed files
- test results
- verification result
- evaluation scores
- latency/cost metrics when available
- final decision
- failure reason
- extracted lesson

## Safety rules

1. The Control Plane cannot directly execute arbitrary host shell commands.
2. Agents operate inside a sandbox/worktree boundary.
3. Promotion requires deterministic checks plus policy evaluation.
4. Live NosTale actions remain outside this control plane and behind the existing client adapter and action validator.
5. Secrets are never stored in source, prompts, artifacts or durable memory unless explicitly classified and protected.

## First implementation milestone

Implement only the domain contracts and run-state model first. Do not add a third-party orchestration framework yet. Once the interfaces are tested, LangGraph can be evaluated as an orchestration backend without changing the core domain model.
