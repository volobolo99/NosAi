# ZMSIA Toolchain Integration

## Purpose

Define how Deep Research, Product Design, Canva, OpenAI, and GitHub participate in one controlled engineering loop. These tools are complementary; none is allowed to become an undocumented source of runtime truth.

## Roles

| Tool | Primary responsibility | Output consumed by |
|---|---|---|
| Deep Research | external knowledge, alternatives, benchmarks, technical evidence | engineering decision records |
| Product Design | UX flows, product behavior, prototype validation | UI implementation/spec |
| Canva | visual architecture, UI concepts, documentation | docs and design references |
| OpenAI | reasoning, coding assistance, analysis, orchestration where justified | provider/tool interfaces |
| GitHub | source of truth for code, issues, reviews, CI, history | every engineering stage |

## Engineering loop

```text
Problem
  -> Deep Research
  -> evidence + alternatives
  -> Architecture Decision Record
  -> Product Design (when user-facing)
  -> Canva visual specification (when useful)
  -> implementation plan
  -> GitHub branch + tests
  -> implementation
  -> CI + evaluation + benchmarks
  -> review
  -> merge/reject
  -> changelog + memory/evidence
```

## Deep Research contract

Research is converted into an auditable engineering record containing:

- question;
- date;
- sources;
- constraints;
- candidate solutions;
- rejected alternatives;
- recommendation;
- expected measurable benefit;
- risks;
- implementation scope.

Research does not directly change code.

## Product Design contract

Product Design is used only for user-facing flows and operational UX. A prototype is not treated as executable behavior. The implementation must translate the approved flow into stable UI contracts and automated tests.

Priority screens for ZMSIA:

1. Runtime dashboard
2. Agent/state monitor
3. Evaluation center
4. Error/diagnostic center
5. Memory explorer
6. Configuration and provider selection
7. Safe-mode and lifecycle controls

## Canva contract

Canva is the visual communication layer:

- architecture diagrams;
- agent maps;
- state/data-flow diagrams;
- dashboard concepts;
- onboarding and technical guides;
- release documentation.

The repository remains the technical source of truth. Any visual artifact used as an implementation reference should have a matching repository document or issue.

## OpenAI integration contract

OpenAI must be isolated behind a provider adapter. The rest of ZMSIA sees a stable internal interface, for example:

```text
request(context, objective, tools, policy)
        -> DecisionProposal
```

The adapter is responsible for model/API details, retries, timeouts, structured output validation, and usage metadata. The safety layer remains outside the model provider.

Recommended routing:

- local provider: low-latency repetitive tasks;
- OpenAI provider: complex reasoning, code analysis/generation, research synthesis, difficult diagnostics;
- mock provider: deterministic tests and regression suites.

## GitHub contract

All implementation changes follow:

1. issue or documented engineering objective;
2. dedicated branch;
3. small commits;
4. automated tests;
5. CI and evaluation;
6. reviewable pull request;
7. merge only after gates pass.

## First implementation sequence

### A. Freeze the baseline

- preserve 4.19.2 behavior;
- capture current test and benchmark results;
- keep the observation-only live-client boundary.

### B. Establish stable contracts

Create typed interfaces for:

- `ObservationProvider`;
- `StateProvider`;
- `DecisionProvider`;
- `ActionValidator`;
- `ActionExecutor`;
- `MemoryStore`;
- `Evaluator`;
- `SafetyPolicy`.

### C. Provider abstraction

Add local/mock/OpenAI provider adapters without changing existing decision semantics. Mock is required before OpenAI is connected to runtime paths.

### D. Orchestration

Introduce a thin orchestrator that coordinates existing goal planning, evaluation, diagnostics, learning, and client boundaries instead of duplicating them.

### E. Evaluation gate

Extend the existing evaluation runner to record provider/model/version, confidence, fallback reason, policy result, and regression identifiers.

### F. Memory evidence

Connect errors, successful solutions, and evaluation reports through typed evidence records. Do not permit automatic production code modification.

### G. UI/design

Only after runtime contracts stabilize, prototype the dashboard and operational workflows with Product Design and Canva.

## Acceptance gates

A stage is accepted only when:

- unit tests pass;
- integration tests pass;
- deterministic evaluation passes;
- no live-client action is triggered by offline tests;
- performance regression is within the agreed budget;
- diagnostics remain machine-readable;
- rollback remains possible.
