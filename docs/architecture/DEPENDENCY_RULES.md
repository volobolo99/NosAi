# NosAi dependency rules

- `data` and `interfaces` are foundational; feature layers must not create reverse dependencies.
- `client` supplies observations and capabilities; it does not own planning or decision policy.
- `perception` produces observations; `world` owns canonical state.
- `decision`, `combat`, and `planning` consume World Model state and never bypass Safety.
- `actions` are executable intents and require Safety Governor approval before client execution.
- `memory` and `learning` consume validated outcomes; they cannot mutate live state directly.
- `simulation` implements compatible interfaces so decision logic can be tested without the real client.
- `performance`, `runtime`, `diagnostics`, and `observability` remain cross-cutting and must not become hidden business-logic dependencies.
- External providers are isolated behind provider contracts.
- No phase may import a concrete implementation from a later phase.
