# Real-client state pipeline

The live path is intentionally layered:

`client observation -> normalized provider data -> CanonicalGameState -> planner`

Providers must not write directly into the planner or world model. Packet, window,
screenshot, replay, and future NosCore adapters normalize their observations first.

`CanonicalGameState` is the stable contract for M1/M2/M3 and future learning code.
The state builder is deterministic and safe to run on recorded observations, which
allows real-client data to become replayable training/evaluation material.

The live client adapter remains observation-first. Action control stays behind the
existing safety governor and must never be inferred from incomplete state.
