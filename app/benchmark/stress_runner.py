from __future__ import annotations
import random
from dataclasses import dataclass, asdict
from statistics import fmean
from .runner import BenchmarkRunner, BenchmarkConfig
from .scenarios import ScenarioEnv, ScenarioSpec, default_scenarios
from .multiobjective import EpisodeOutcome, ObjectiveWeights, summarize, aggregate, MultiObjectiveReport

@dataclass(frozen=True)
class StressConfig:
    episodes_per_scenario: int = 20
    max_steps: int = 12
    simulations: int = 48
    horizon: int = 5
    seed: int = 42
    weights: ObjectiveWeights = ObjectiveWeights()

@dataclass(frozen=True)
class StressResult:
    level: str
    report: MultiObjectiveReport

    def to_dict(self) -> dict:
        return {"level": self.level, "report": self.report.to_dict()}

class StressBenchmarkRunner:
    LEVELS = ("baseline", "m1", "m2", "m3", "m4")

    def __init__(self, config: StressConfig | None = None, scenarios: tuple[ScenarioSpec, ...] | None = None):
        self.config = config or StressConfig()
        self.scenarios = scenarios or default_scenarios()

    def _choose(self, level, stack, agent, state, actions):
        if stack is None or level == "m1":
            return agent.choose(state, actions), None
        result = stack.choose(state, actions)
        if level == "m4":
            return result.action, result.adaptation.regime.value
        return result[0], None

    def run_level(self, level: str) -> StressResult:
        base = BenchmarkRunner(BenchmarkConfig("stress", seed=self.config.seed, episodes=1, max_steps=self.config.max_steps, simulations=self.config.simulations, horizon=self.config.horizon))
        stack, agent = base._make_stack(level)
        scenario_metrics = []
        for spec in self.scenarios:
            outcomes = []
            for episode in range(self.config.episodes_per_scenario):
                random.seed(self.config.seed + episode)
                env = ScenarioEnv(spec)
                state = env.reset()
                total = 0.0
                risk = 0.0
                done = False
                steps = 0
                for _ in range(self.config.max_steps):
                    actions = env.actions(state)
                    if not actions:
                        break
                    action, _ = self._choose(level, stack, agent, state, actions)
                    if action is None:
                        break
                    next_state, reward, done, info = env.step(state, action)
                    total += reward
                    risk += float(info.get("risk", 0.0))
                    steps += 1
                    agent.update_raw(state, action, reward, next_state, done, env.actions(next_state))
                    owner = base._m1_owner(stack)
                    if owner is not None:
                        owner.observe_transition(state, action, next_state, reward, done)
                    state = next_state
                    if done:
                        break
                outcomes.append(EpisodeOutcome(total, steps, done and not bool(info.get("player_dead", False)), risk, spec.ood, spec.shift))
            scenario_metrics.append(summarize(spec.name, outcomes, self.config.weights, self.config.max_steps))
        return StressResult(level, aggregate(scenario_metrics))

    def run(self) -> tuple[StressResult, ...]:
        return tuple(self.run_level(level) for level in self.LEVELS)
