# NosAi — Local Secondary AI Architecture

## Purpose

NosAi now has an explicit integration boundary for a **secondary on-device AI**.
This is an architectural scaffold, not the final local model implementation.

## Position in the system

```text
                 ┌──────────────────────────┐
                 │   NosAi Primary Brain    │
                 │ planner / orchestrator   │
                 └────────────┬─────────────┘
                              │
                       routing / policy
                              │
              ┌──────────────┴──────────────┐
              │                             │
      Primary inference              Secondary local AI
                                      router boundary
                                            │
                              future backend adapter
                                            │
                              local model / runtime
                                            │
                         Windows CPU / GPU / RAM / VRAM

        AutoSet + Benchmark ───────► resource/model selection
        Dashboard ──────────────────► health / latency / resources
        Test Center + CI ───────────► contract + integration tests
```

## Design decisions

- The local AI is **secondary**, not a replacement for the primary brain.
- It is disabled by default until a concrete backend is validated.
- The orchestrator talks to a stable router contract rather than directly to a
  model runtime.
- Backend choice remains open so the later implementation can use an
  appropriate local runtime without redesigning the architecture.
- AutoSet and benchmark results are first-class inputs to future model and
  resource selection.
- Dashboard observability is part of the contract from the beginning.
- Fallback and parallel-consultation policies remain explicit configuration
  switches and are not silently enabled.

## Next implementation phase

1. Detect the actual Windows hardware profile.
2. Benchmark candidate local runtimes/models.
3. Select the best backend/model for the machine.
4. Implement the concrete backend adapter.
5. Connect the router to the main orchestrator.
6. Add confidence/fallback policy and resource limits.
7. Expose status, model, latency and resource usage in the dashboard.
8. Add Test Center / CI coverage for the local-AI contract.

The architecture is intentionally ready for the detailed specifications that
will be defined in the next development phase.
