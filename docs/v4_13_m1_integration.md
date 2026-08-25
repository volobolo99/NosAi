# v4.13 M1 integration

M1-1..M1-10 are integrated into the v4.8 Reward Learning Loop as an optional layer.
The legacy loop remains compatible when `m1_stack=None`.

## M1 modules
- Curriculum Learning
- Self-Play contracts
- Prioritized Experience Replay
- Distribution Shift Detection
- OOD Detection
- Experience Quality Scoring
- Dataset Registry
- Data Validation
- World Model Ensemble
- Latent World Model

## Integration boundary
`app/m1/adapters.py` converts the historical `WorldState`/`WorldAction` types into the normalized M1 contracts. `SandboxWorldModel` reuses the existing deterministic sandbox; it does not control a live client.

`LearningLoop(..., m1_stack=M1LearningStack(reference_features))` activates observation, validation, quality scoring, replay, OOD and shift telemetry while preserving the existing RL/reward path.

## Compatibility
The v4.0/v4.1 architecture requires domain/infrastructure separation, dependency injection, deterministic replay/simulation, versioned schemas and systematic unit/integration testing. M1 follows the same boundary by exposing adapters instead of importing infrastructure into the M1 contracts.
