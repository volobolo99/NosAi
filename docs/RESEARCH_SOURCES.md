# External AI Research Sources

Research reviewed for the NosAi brain roadmap (2026-08-26).

| Project | Use in NosAi | Decision |
|---|---|---|
| Farama Gymnasium | Standard RL environment interface | Adopt interface; do not copy internals |
| DLR-RM Stable-Baselines3 | PPO and other mature RL implementations | Optional dependency for training |
| SB3-Contrib | Experimental RL algorithms | Evaluate only when baseline needs it |
| CleanRL | Small reference implementations | Use for learning/verification, not as a core dependency |
| RL Baselines3 Zoo | Experiment/evaluation patterns | Reuse methodology where appropriate |
| PettingZoo | Multi-agent environment API | Future raid/team phase |

## Reuse rules
- Verify license before copying code.
- Prefer dependency + adapter over vendoring.
- Keep third-party code isolated from NosAi domain logic.
- Record source and license in this file when code is materially reused.
- Benchmark every imported component against a simple internal baseline.

## Current architectural conclusion
The strongest near-term combination is a custom NosAi canonical state model + deterministic safety/strategy + bounded memory/replay + Gymnasium-compatible simulator + Stable-Baselines3 training adapter. Vision and live control remain separate layers.
