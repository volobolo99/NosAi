from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from math import exp


class PlannerRegime(str, Enum):
    FAST = "fast"
    BALANCED = "balanced"
    DEEP = "deep"
    CAUTIOUS = "cautious"


@dataclass(frozen=True)
class AdaptiveDecision:
    regime: PlannerRegime
    simulations: int
    horizon: int
    risk_penalty: float
    uncertainty_penalty: float
    confidence: float
    features: dict[str, float]


class AdaptivePlanner:
    """Deterministic controller that adapts planning budget to model state.

    It does not learn from a single reward sample. The optional ``update`` method
    performs a bounded online update of regime preferences from observed utility,
    keeping planning stable and reproducible.
    """

    def __init__(self, *, seed: int = 42, min_simulations: int = 16,
                 max_simulations: int = 256, min_horizon: int = 2,
                 max_horizon: int = 12, learning_rate: float = 0.03):
        if min_simulations <= 0 or max_simulations < min_simulations:
            raise ValueError("invalid simulation bounds")
        if min_horizon <= 0 or max_horizon < min_horizon:
            raise ValueError("invalid horizon bounds")
        self.seed = seed
        self.min_simulations = min_simulations
        self.max_simulations = max_simulations
        self.min_horizon = min_horizon
        self.max_horizon = max_horizon
        self.learning_rate = learning_rate
        self._bias = {r: 0.0 for r in PlannerRegime}

    @staticmethod
    def _sigmoid(x: float) -> float:
        return 1.0 / (1.0 + exp(-max(-30.0, min(30.0, x))))

    def decide(self, *, uncertainty: float = 0.0, ood: float = 0.0,
               shift: float = 0.0, causal_confidence: float = 0.0,
               memory_confidence: float = 0.0, action_count: int = 1,
               horizon_hint: int | None = None) -> AdaptiveDecision:
        u = max(0.0, min(1.0, float(uncertainty)))
        o = max(0.0, min(1.0, float(ood)))
        s = max(0.0, min(1.0, float(shift)))
        c = max(0.0, min(1.0, float(causal_confidence)))
        m = max(0.0, min(1.0, float(memory_confidence)))
        complexity = max(0.0, min(1.0, (max(1, action_count) - 1) / 15.0))
        pressure = 0.45 * u + 0.30 * o + 0.25 * s
        evidence = 0.55 * c + 0.45 * m

        scores = {
            PlannerRegime.FAST: 1.0 - pressure - 0.25 * complexity,
            PlannerRegime.BALANCED: 0.65 - 0.15 * pressure + 0.15 * evidence,
            PlannerRegime.DEEP: 0.35 + 0.85 * pressure + 0.25 * complexity + 0.10 * evidence,
            PlannerRegime.CAUTIOUS: 0.20 + 1.10 * pressure + 0.30 * (1.0 - evidence),
        }
        scores = {k: v + self._bias[k] for k, v in scores.items()}
        regime = max(scores, key=scores.get)
        confidence = self._sigmoid(abs(scores[regime] - sorted(scores.values())[-2]) * 4.0)

        if regime is PlannerRegime.FAST:
            sim_factor, horizon_factor = 0.25, 0.35
        elif regime is PlannerRegime.BALANCED:
            sim_factor, horizon_factor = 0.50, 0.55
        elif regime is PlannerRegime.DEEP:
            sim_factor, horizon_factor = 0.90, 0.90
        else:
            sim_factor, horizon_factor = 0.75, 1.0

        simulations = round(self.min_simulations + (self.max_simulations - self.min_simulations) * sim_factor)
        horizon = round(self.min_horizon + (self.max_horizon - self.min_horizon) * horizon_factor)
        if horizon_hint is not None:
            horizon = min(horizon, max(self.min_horizon, int(horizon_hint)))

        return AdaptiveDecision(
            regime, simulations, horizon,
            risk_penalty=0.10 + 0.35 * (u + o) / 2.0,
            uncertainty_penalty=0.10 + 0.40 * (u + s) / 2.0,
            confidence=confidence,
            features={"uncertainty": u, "ood": o, "shift": s,
                      "causal_confidence": c, "memory_confidence": m,
                      "complexity": complexity},
        )

    def update(self, decision: AdaptiveDecision, utility: float) -> None:
        """Bounded bandit-style update; no unbounded weight growth."""
        reward = max(-1.0, min(1.0, float(utility)))
        for regime in self._bias:
            target = reward if regime is decision.regime else 0.0
            self._bias[regime] = max(-1.0, min(1.0,
                self._bias[regime] + self.learning_rate * (target - self._bias[regime])))

    def snapshot(self) -> dict[str, float]:
        return {r.value: self._bias[r] for r in PlannerRegime}
