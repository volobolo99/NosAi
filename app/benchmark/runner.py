from __future__ import annotations

import json
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from app.world_model.state import WorldState, EntityState
from app.world_model.actions import WorldAction
from app.rl.q_learning import QLearningAgent
from app.m1.integration import M1LearningStack
from app.m2.integration import M2PlanningStack
from app.m3.integration import M3PlanningStack
from app.m4.integration import M4PlanningStack


class BenchmarkGoalEnv:
    """Small deterministic WorldState environment shared by every ablation level."""

    def reset(self) -> WorldState:
        return WorldState(
            tick=0,
            character={"hp": 100.0, "mp": 50.0},
            entities={"mob:1": EntityState("mob:1", "mob", {"hp": 20.0})},
            map_id="benchmark",
        )

    def actions(self, state: WorldState) -> list[WorldAction]:
        target = state.entities.get("mob:1")
        hp = float(target.attributes.get("hp", 0.0)) if target else 0.0
        if hp <= 0:
            return []
        return [
            WorldAction("attack5", "ATTACK", {"target_id": "mob:1", "damage": 5.0}),
            WorldAction("attack10", "ATTACK", {"target_id": "mob:1", "damage": 10.0}),
        ]

    def step(self, state: WorldState, action: WorldAction):
        next_state = state.copy()
        next_state.tick += 1
        target = next_state.entities.get("mob:1")
        if target is None:
            return next_state, -1.0, True
        damage = float(action.parameters.get("damage", 0.0))
        target = EntityState(target.entity_id, target.entity_type, dict(target.attributes))
        hp = max(0.0, float(target.attributes.get("hp", 0.0)) - damage)
        target.attributes["hp"] = hp
        next_state.entities[target.entity_id] = target
        done = hp <= 0.0
        # Same reward semantics as the historical SandboxWorldModel.
        reward = 1.0 + (10.0 if done else 0.0)
        return next_state, reward, done


@dataclass(frozen=True)
class BenchmarkConfig:
    name: str
    seed: int = 42
    episodes: int = 25
    max_steps: int = 10
    simulations: int = 32
    horizon: int = 3


@dataclass(frozen=True)
class BenchmarkMetrics:
    episodes: int
    mean_reward: float
    reward_std: float
    success_rate: float
    mean_steps: float
    wall_time_s: float
    decisions: int
    m4_regime_counts: dict[str, int]


@dataclass(frozen=True)
class BenchmarkResult:
    config: str
    metrics: BenchmarkMetrics


@dataclass(frozen=True)
class BenchmarkReport:
    baseline: BenchmarkResult
    ablations: tuple[BenchmarkResult, ...]
    deltas: dict[str, dict[str, float]]

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")


class BenchmarkRunner:
    """Deterministic benchmark and ablation harness for baseline through M4."""

    @staticmethod
    def _reference_features() -> tuple[float, ...]:
        return (0.0, 100.0, 50.0, 0.0, 1.0, 20.0)

    def __init__(self, config: BenchmarkConfig):
        self.config = config

    def _make_stack(self, level: str):
        agent = QLearningAgent(epsilon=0.0, seed=self.config.seed)
        if level == "baseline":
            return None, agent
        m1 = M1LearningStack(self._reference_features(), seed=self.config.seed)
        if level == "m1":
            return m1, agent
        m2 = M2PlanningStack(m1, simulations=self.config.simulations, horizon=self.config.horizon, seed=self.config.seed)
        if level == "m2":
            return m2, agent
        m3 = M3PlanningStack(m2, seed=self.config.seed)
        if level == "m3":
            return m3, agent
        if level == "m4":
            return M4PlanningStack(m3, seed=self.config.seed, horizon=self.config.horizon), agent
        raise ValueError(f"unknown benchmark level: {level}")

    @staticmethod
    def _m1_owner(stack):
        if isinstance(stack, M1LearningStack):
            return stack
        if isinstance(stack, M2PlanningStack):
            return stack.m1_stack
        if isinstance(stack, M3PlanningStack):
            return stack.m2_stack.m1_stack
        if isinstance(stack, M4PlanningStack):
            return stack.m3_stack.m2_stack.m1_stack
        return None

    def run_level(self, level: str) -> BenchmarkResult:
        stack, agent = self._make_stack(level)
        rewards: list[float] = []
        steps: list[int] = []
        successes = 0
        decisions = 0
        regimes: dict[str, int] = {}
        started = time.perf_counter()

        for _ in range(self.config.episodes):
            env = BenchmarkGoalEnv()
            state = env.reset()
            total = 0.0
            episode_steps = 0
            done = False
            for _ in range(self.config.max_steps):
                actions = env.actions(state)
                if not actions:
                    break
                if stack is None or level == "m1":
                    action = agent.choose(state, actions)
                else:
                    result = stack.choose(state, actions)
                    if level == "m4":
                        action = result.action
                        regime = result.adaptation.regime.value
                        regimes[regime] = regimes.get(regime, 0) + 1
                    else:
                        action = result[0]
                    decisions += 1
                if action is None:
                    break
                next_state, reward, done = env.step(state, action)
                total += float(reward)
                episode_steps += 1
                agent.update_raw(state, action, reward, next_state, done, env.actions(next_state))
                owner = self._m1_owner(stack)
                if owner is not None:
                    owner.observe_transition(state, action, next_state, reward, done)
                state = next_state
                if done:
                    break
            rewards.append(total)
            steps.append(episode_steps)
            successes += int(done)

        elapsed = time.perf_counter() - started
        metrics = BenchmarkMetrics(
            episodes=self.config.episodes,
            mean_reward=statistics.fmean(rewards),
            reward_std=statistics.pstdev(rewards) if len(rewards) > 1 else 0.0,
            success_rate=successes / max(1, self.config.episodes),
            mean_steps=statistics.fmean(steps),
            wall_time_s=elapsed,
            decisions=decisions,
            m4_regime_counts=regimes,
        )
        return BenchmarkResult(level, metrics)

    def run_ablation(self, levels: Iterable[str] = ("baseline", "m1", "m2", "m3", "m4")) -> BenchmarkReport:
        results = [self.run_level(level) for level in levels]
        baseline = results[0]
        base = baseline.metrics
        deltas: dict[str, dict[str, float]] = {}
        for result in results[1:]:
            m = result.metrics
            deltas[result.config] = {
                "mean_reward_delta": m.mean_reward - base.mean_reward,
                "success_rate_delta": m.success_rate - base.success_rate,
                "mean_steps_delta": m.mean_steps - base.mean_steps,
                "wall_time_delta_s": m.wall_time_s - base.wall_time_s,
            }
        return BenchmarkReport(baseline, tuple(results[1:]), deltas)
