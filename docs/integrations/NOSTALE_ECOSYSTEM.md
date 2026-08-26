# NosTale ecosystem integration

NosAi uses external NosTale projects as **references and optional providers**, not as runtime dependencies.

## Sources

| Source | Role in NosAi | Integration policy |
| --- | --- | --- |
| NosCore | Primary reference for game entities, packet semantics and server-side state | Adapt into canonical contracts; do not fork the server |
| NosCore.Packets | Primary packet/serialization reference | Adapt decoded packets into `PacketEnvelope` |
| NosCore.Algorithm | Algorithm/reference material | Reuse concepts only after benchmark and license review |
| ChickenAPI | Architecture/plugin/event/entity reference | Use as design reference; no direct runtime dependency |
| NosSmooth | Bot/action/pathfinding reference | Adapt command/pathfinding concepts behind action contracts |

## Boundary

All external data enters through `app.integrations.nostale_ecosystem` and is
translated to `PacketEnvelope`, `EntitySnapshot`, or `GameStateSnapshot`.
The World Model consumes the canonical state and never imports a concrete
external project.

This preserves the project's dependency rule that external providers stay
behind provider contracts.

## Licensing

Before copying code, generated packet definitions, or assets from an external
repository into NosAi, record the exact upstream repository, revision and
license. Prefer clean-room adapters around documented/public interfaces.
Do not introduce a dependency merely because a source contains a useful
implementation.

## Current limitation

The current adapter is intentionally schema-level. It does **not** claim that
NosCore packets are automatically decoded from a live NosTale client. A live
packet decoder/transport remains a separate provider implementation and must be
validated against the actual client build before enabling execution.
