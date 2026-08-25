from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any, Iterable


@dataclass
class AgentRecord:
    agent_id: str
    policy: Any = None
    policy_version: int = 1
    status: str = "active"
    wins: int = 0
    losses: int = 0
    draws: int = 0
    rating: float = 1000.0
    matches: int = 0
    promotions: int = 0
    demotions: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def games(self) -> int:
        return self.wins + self.losses + self.draws

    @property
    def win_rate(self) -> float:
        return (self.wins + 0.5 * self.draws) / self.games if self.games else 0.0


@dataclass(frozen=True)
class OpponentProfile:
    agent_id: str
    aggression: float
    consistency: float
    estimated_strength: float
    confidence: float


@dataclass(frozen=True)
class MatchResult:
    winner: str | None
    loser: str | None
    draw: bool = False


class LeagueManager:
    """Persistent population manager for champion/challenger policy evaluation.

    The manager owns lifecycle, rating, match accounting, opponent selection and
    promotion/demotion. Policies themselves remain opaque so the league can host
    heuristic, RL or neural policies without coupling to a training framework.
    """

    def __init__(
        self,
        k_factor: float = 32.0,
        initial_rating: float = 1000.0,
        promotion_delta: float = 50.0,
        demotion_delta: float = 100.0,
        min_games_for_promotion: int = 5,
    ):
        if k_factor <= 0:
            raise ValueError("k_factor must be positive")
        if min_games_for_promotion < 1:
            raise ValueError("min_games_for_promotion must be >= 1")
        self.agents: dict[str, AgentRecord] = {}
        self.k_factor = float(k_factor)
        self.initial_rating = float(initial_rating)
        self.promotion_delta = float(promotion_delta)
        self.demotion_delta = float(demotion_delta)
        self.min_games_for_promotion = int(min_games_for_promotion)
        self._champion_id: str | None = None

    def register(self, agent_id: str, policy: Any = None, *, policy_version: int = 1, metadata: dict[str, Any] | None = None) -> AgentRecord:
        if not agent_id:
            raise ValueError("agent_id must be non-empty")
        if agent_id not in self.agents:
            self.agents[agent_id] = AgentRecord(
                agent_id=agent_id,
                policy=policy,
                policy_version=int(policy_version),
                rating=self.initial_rating,
                metadata=dict(metadata or {}),
            )
        else:
            record = self.agents[agent_id]
            if policy is not None:
                record.policy = policy
            if policy_version != record.policy_version:
                record.policy_version = int(policy_version)
        if self._champion_id is None:
            self._champion_id = agent_id
        return self.agents[agent_id]

    def unregister(self, agent_id: str, *, retire: bool = True) -> None:
        if agent_id not in self.agents:
            raise KeyError(agent_id)
        if retire:
            self.retire(agent_id)
        else:
            del self.agents[agent_id]
            if self._champion_id == agent_id:
                self._champion_id = self._best_active_id()

    def retire(self, agent_id: str) -> AgentRecord:
        record = self.agents[agent_id]
        record.status = "retired"
        if self._champion_id == agent_id:
            self._champion_id = self._best_active_id(exclude=agent_id)
        return record

    def activate(self, agent_id: str) -> AgentRecord:
        record = self.agents[agent_id]
        record.status = "active"
        if self._champion_id is None:
            self._champion_id = agent_id
        return record

    def update_policy(self, agent_id: str, policy: Any, *, version: int | None = None) -> AgentRecord:
        record = self.agents[agent_id]
        record.policy = policy
        record.policy_version = record.policy_version + 1 if version is None else int(version)
        return record

    def record(self, result: MatchResult) -> None:
        if result.winner is None or result.loser is None:
            return
        if result.winner == result.loser:
            raise ValueError("an agent cannot play against itself")
        if result.winner not in self.agents or result.loser not in self.agents:
            raise KeyError("both match participants must be registered")
        w, l = self.agents[result.winner], self.agents[result.loser]
        if w.status == "retired" or l.status == "retired":
            raise ValueError("retired agents cannot enter new matches")
        expected_w = 1.0 / (1.0 + 10 ** ((l.rating - w.rating) / 400.0))
        expected_l = 1.0 - expected_w
        w.matches += 1; l.matches += 1
        if result.draw:
            w.draws += 1; l.draws += 1
            w.rating += self.k_factor * (0.5 - expected_w)
            l.rating += self.k_factor * (0.5 - expected_l)
        else:
            w.wins += 1; l.losses += 1
            w.rating += self.k_factor * (1.0 - expected_w)
            l.rating += self.k_factor * (0.0 - expected_l)
        self._update_champion()

    def leaderboard(self, *, active_only: bool = True) -> list[AgentRecord]:
        records = self.agents.values()
        if active_only:
            records = (a for a in records if a.status != "retired")
        return sorted(records, key=lambda a: (a.rating, a.win_rate, -a.games), reverse=True)

    def champion(self) -> AgentRecord | None:
        if self._champion_id is None:
            self._champion_id = self._best_active_id()
        return self.agents.get(self._champion_id) if self._champion_id else None

    def challenger_pool(self, *, limit: int = 3) -> list[AgentRecord]:
        if limit < 1:
            return []
        champion_id = self.champion().agent_id if self.champion() else None
        return [a for a in self.leaderboard() if a.agent_id != champion_id][:limit]

    def select_opponents(self, agent_id: str, *, count: int = 1, strategy: str = "balanced") -> list[AgentRecord]:
        if agent_id not in self.agents:
            raise KeyError(agent_id)
        if count <= 0:
            return []
        candidates = [a for a in self.leaderboard() if a.agent_id != agent_id]
        if strategy == "strongest":
            return candidates[:count]
        if strategy == "underplayed":
            return sorted(candidates, key=lambda a: (a.games, -a.rating))[:count]
        if strategy != "balanced":
            raise ValueError("strategy must be balanced, strongest or underplayed")
        source = self.agents[agent_id]
        return sorted(candidates, key=lambda a: (abs(a.rating - source.rating), a.games))[:count]

    def promote_challenger(self, challenger_id: str) -> bool:
        champion = self.champion()
        challenger = self.agents.get(challenger_id)
        if champion is None or challenger is None or challenger.status != "active":
            return False
        if challenger_id == champion.agent_id:
            return False
        if challenger.games < self.min_games_for_promotion:
            return False
        if challenger.rating < champion.rating + self.promotion_delta:
            return False
        old = champion
        old.status = "challenger"
        old.demotions += 1
        challenger.promotions += 1
        self._champion_id = challenger_id
        return True

    def demote_if_needed(self, agent_id: str) -> bool:
        record = self.agents[agent_id]
        champion = self.champion()
        if champion is None or record.agent_id == champion.agent_id:
            return False
        if record.games < self.min_games_for_promotion:
            return False
        if record.rating < champion.rating - self.demotion_delta:
            record.status = "challenger"
            record.demotions += 1
            return True
        return False

    def evaluate_promotion(self, challenger_id: str) -> bool:
        promoted = self.promote_challenger(challenger_id)
        if promoted:
            return True
        self.demote_if_needed(challenger_id)
        return False

    def _best_active_id(self, exclude: str | None = None) -> str | None:
        active = [a for a in self.agents.values() if a.status != "retired" and a.agent_id != exclude]
        return max(active, key=lambda a: (a.rating, a.win_rate), default=None).agent_id if active else None

    def _update_champion(self) -> None:
        champion = self.champion()
        if champion is None:
            self._champion_id = self._best_active_id()
            return
        best = self._best_active_id()
        if best is not None and self.agents[best].rating > champion.rating + self.promotion_delta:
            self.promote_challenger(best)

    def snapshot(self) -> dict[str, Any]:
        return {
            "config": {
                "k_factor": self.k_factor,
                "initial_rating": self.initial_rating,
                "promotion_delta": self.promotion_delta,
                "demotion_delta": self.demotion_delta,
                "min_games_for_promotion": self.min_games_for_promotion,
            },
            "champion_id": self._champion_id,
            "agents": [
                {k: v for k, v in asdict(a).items() if k != "policy"}
                | {"policy": a.policy if isinstance(a.policy, (str, int, float, bool, type(None), dict, list)) else None}
                for a in self.agents.values()
            ],
        }

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.snapshot(), indent=2, sort_keys=True), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path, *, policies: dict[str, Any] | None = None) -> "LeagueManager":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        league = cls(**payload.get("config", {}))
        for raw in payload.get("agents", []):
            policy = (policies or {}).get(raw["agent_id"], raw.get("policy"))
            raw = dict(raw)
            raw.pop("policy", None)
            league.agents[raw["agent_id"]] = AgentRecord(policy=policy, **raw)
        league._champion_id = payload.get("champion_id")
        if league._champion_id not in league.agents:
            league._champion_id = league._best_active_id()
        return league


class OpponentModel:
    """Online opponent model with recency-weighted behavioral statistics."""

    def __init__(self, decay: float = 0.85, prior_strength: float = 2.0):
        if not 0.0 < decay <= 1.0:
            raise ValueError("decay must be in (0, 1]")
        self.decay = float(decay)
        self.prior_strength = float(prior_strength)
        self._history: dict[str, list[dict[str, float]]] = {}

    def observe(self, agent_id: str, observation: dict[str, float]) -> None:
        self._history.setdefault(agent_id, []).append(dict(observation))

    def observe_many(self, agent_id: str, history: Iterable[dict[str, float]]) -> None:
        for row in history:
            self.observe(agent_id, row)

    def history(self, agent_id: str) -> list[dict[str, float]]:
        return list(self._history.get(agent_id, []))

    def profile(self, agent_id: str, history: Iterable[dict[str, float]] | None = None) -> OpponentProfile:
        explicit_history = history is not None
        rows = list(history) if explicit_history else self.history(agent_id)
        if not rows:
            return OpponentProfile(agent_id, .5, .5, 1000.0, 0.0)
        # Preserve the legacy batch API exactly; online observations use the
        # recency-weighted path below.
        if explicit_history:
            aggression = max(0.0, min(1.0, mean(float(r.get('aggression', .5)) for r in rows)))
            variance = max(0.0, min(1.0, mean(float(r.get('variance', .5)) for r in rows)))
            strength = mean(float(r.get('rating', 1000.0)) for r in rows)
            confidence = min(1.0, len(rows) / 20.0)
            return OpponentProfile(agent_id, aggression, 1.0 - variance, strength, confidence)
        weights = [self.decay ** (len(rows) - 1 - i) for i in range(len(rows))]
        total = sum(weights) + self.prior_strength

        def weighted(key: str, default: float) -> float:
            numerator = self.prior_strength * default
            for weight, row in zip(weights, rows):
                numerator += weight * float(row.get(key, default))
            return numerator / total

        aggression = max(0.0, min(1.0, weighted('aggression', .5)))
        variance = max(0.0, min(1.0, weighted('variance', .5)))
        consistency = 1.0 - variance
        strength = weighted('rating', 1000.0)
        confidence = min(1.0, sum(weights) / (sum(weights) + self.prior_strength))
        return OpponentProfile(agent_id, aggression, consistency, strength, confidence)

    def predict(self, agent_id: str, *, aggression_weight: float = .6) -> dict[str, float]:
        profile = self.profile(agent_id)
        aggression_weight = max(0.0, min(1.0, aggression_weight))
        return {
            "aggression": profile.aggression,
            "consistency": profile.consistency,
            "strength": profile.estimated_strength,
            "confidence": profile.confidence,
            "risk_index": aggression_weight * profile.aggression + (1.0 - aggression_weight) * (1.0 - profile.consistency),
        }

    def reset(self, agent_id: str) -> None:
        self._history.pop(agent_id, None)


@dataclass(frozen=True)
class EvolutionConfig:
    population_size: int = 4
    elite_count: int = 1
    generations: int = 3
    mutation_rate: float = 0.25


class SelfPlayEvaluator:
    def evaluate(self, league: LeagueManager, matches: Iterable[MatchResult]) -> dict[str, float]:
        before = {k: a.rating for k, a in league.agents.items()}
        for match in matches:
            league.record(match)
        return {k: league.agents[k].rating - before.get(k, league.initial_rating) for k in league.agents}


class SelfPlayEvolution:
    """Deterministic policy-population evolution around the league manager.

    ``mutate`` and ``play_generation`` are injected so the engine is independent
    of a specific neural/RL policy representation.
    """

    def __init__(self, league: LeagueManager, config: EvolutionConfig | None = None):
        self.league = league
        self.config = config or EvolutionConfig()
        if self.config.population_size < 2:
            raise ValueError("population_size must be >= 2")
        if not 1 <= self.config.elite_count < self.config.population_size:
            raise ValueError("elite_count must be in [1, population_size)")
        if self.config.generations < 1:
            raise ValueError("generations must be >= 1")
        if not 0.0 <= self.config.mutation_rate <= 1.0:
            raise ValueError("mutation_rate must be in [0, 1]")

    def seed(self, policies: dict[str, Any]) -> None:
        for agent_id, policy in policies.items():
            self.league.register(agent_id, policy=policy)

    def generation(self, play_generation: Any) -> list[AgentRecord]:
        active = self.league.leaderboard()[: self.config.population_size]
        if len(active) < 2:
            raise ValueError("at least two active agents are required")
        results = play_generation(active)
        for result in results:
            self.league.record(result)
        return self.league.leaderboard()[: self.config.population_size]

    def evolve(self, mutate: Any, play_generation: Any) -> list[AgentRecord]:
        for _ in range(self.config.generations):
            ranked = self.generation(play_generation)
            elites = ranked[: self.config.elite_count]
            if not elites:
                break
            for index in range(self.config.elite_count, self.config.population_size):
                parent = elites[index % len(elites)]
                child_id = f"{parent.agent_id}:g{parent.policy_version + 1}:{index}"
                child_policy = mutate(parent.policy, self.config.mutation_rate, index)
                self.league.register(child_id, policy=child_policy, policy_version=parent.policy_version + 1)
        return self.league.leaderboard()[: self.config.population_size]


@dataclass(frozen=True)
class PolicyEvaluation:
    agent_id: str
    games: int
    wins: int
    draws: int
    losses: int
    score: float
    win_rate: float
    draw_rate: float
    loss_rate: float
    standard_error: float
    confidence: float


class PolicyEvaluator:
    """Evaluate a policy from match outcomes with uncertainty and coverage.

    The evaluator is deliberately independent of a policy implementation: it
    consumes immutable match results and exposes both the legacy scalar score
    and a full evaluation record suitable for league selection, benchmarking
    and downstream planner decisions.
    """

    def evaluate(self, results: Iterable[MatchResult], agent_id: str) -> PolicyEvaluation:
        if not agent_id:
            raise ValueError("agent_id must be non-empty")
        rows = list(results)
        wins = sum(r.winner == agent_id and not r.draw for r in rows)
        draws = sum(r.draw and (r.winner == agent_id or r.loser == agent_id or (r.winner is None and r.loser is None)) for r in rows)
        losses = sum(r.loser == agent_id and not r.draw for r in rows)
        games = wins + draws + losses
        if games == 0:
            return PolicyEvaluation(agent_id, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        score = (wins + 0.5 * draws) / games
        win_rate = wins / games
        draw_rate = draws / games
        loss_rate = losses / games
        # Use a weak Beta(1, 1) prior so uncertainty remains non-zero even
        # for all-win/all-loss samples; this prevents overconfidence from
        # perfectly separated short matches.
        posterior_p = (score * games + 0.5) / (games + 1.0)
        posterior_variance = posterior_p * (1.0 - posterior_p) / (games + 2.0)
        standard_error = math.sqrt(max(0.0, posterior_variance))
        confidence = min(1.0, math.sqrt(games / 25.0))
        return PolicyEvaluation(
            agent_id, games, wins, draws, losses, score, win_rate, draw_rate,
            loss_rate, standard_error, confidence
        )

    def score(self, results: Iterable[MatchResult], agent_id: str) -> float:
        # Legacy API: score is now based only on games involving agent_id,
        # rather than being diluted by unrelated matches in the same batch.
        return self.evaluate(results, agent_id).score

    def compare(self, left: PolicyEvaluation, right: PolicyEvaluation) -> dict[str, float]:
        if left.games == 0 or right.games == 0:
            raise ValueError("both policies need at least one evaluated game")
        delta = left.score - right.score
        pooled_se = math.sqrt(left.standard_error ** 2 + right.standard_error ** 2)
        z = delta / pooled_se if pooled_se > 0 else 0.0
        return {
            "score_delta": delta,
            "pooled_standard_error": pooled_se,
            "z_score": z,
            "left_confidence": left.confidence,
            "right_confidence": right.confidence,
        }


@dataclass(frozen=True)
class MultiAgentAction:
    action_id: str
    base_score: float
    matchup_score: float = 0.0
    risk: float = 0.0
    information_gain: float = 0.0


@dataclass(frozen=True)
class MultiAgentPlanResult:
    action_id: str
    score: float
    opponent_id: str
    opponent_risk: float
    opponent_confidence: float
    rationale: str


class MultiAgentPlanner:
    """Opponent-aware action planner backed by the live league and evaluation state.

    The planner does not merely add a fixed aggression bonus. It combines the
    candidate action's intrinsic score with matchup evidence, opponent risk,
    opponent-model confidence, policy evaluation confidence and information
    gain. This keeps the planner useful for heuristic, RL and neural policies.
    """

    def __init__(
        self,
        opponent_model: OpponentModel | None = None,
        league: LeagueManager | None = None,
        evaluator: PolicyEvaluator | None = None,
        *,
        risk_weight: float = 0.20,
        matchup_weight: float = 0.35,
        information_weight: float = 0.10,
    ):
        self.opponent_model = opponent_model or OpponentModel()
        self.league = league
        self.evaluator = evaluator or PolicyEvaluator()
        self.risk_weight = float(risk_weight)
        self.matchup_weight = float(matchup_weight)
        self.information_weight = float(information_weight)
        if min(self.risk_weight, self.matchup_weight, self.information_weight) < 0:
            raise ValueError("planner weights must be non-negative")

    def adjust(self, base_scores: dict[str, float], profile: OpponentProfile) -> dict[str, float]:
        # Preserve the legacy API while making the adjustment bounded by the
        # confidence of the opponent model.
        bonus = (.15 * profile.aggression + .10 * profile.consistency) * profile.confidence
        return {k: v + bonus for k, v in base_scores.items()}

    def _evaluation_confidence(self, agent_id: str | None) -> float:
        if self.league is None or not agent_id or agent_id not in self.league.agents:
            return 0.0
        record = self.league.agents[agent_id]
        return min(1.0, math.sqrt(record.games / 25.0))

    def plan(
        self,
        actions: Iterable[MultiAgentAction],
        *,
        opponent_id: str,
        agent_id: str | None = None,
    ) -> MultiAgentPlanResult:
        candidates = list(actions)
        if not candidates:
            raise ValueError("at least one action is required")
        if not opponent_id:
            raise ValueError("opponent_id must be non-empty")

        profile = self.opponent_model.profile(opponent_id)
        eval_conf = self._evaluation_confidence(agent_id)
        scored: list[tuple[float, MultiAgentAction]] = []
        for action in candidates:
            # Aggressive opponents increase the value of actions that have a
            # strong matchup profile, while risk is explicitly penalised.
            matchup = action.matchup_score * self.matchup_weight
            opponent_pressure = profile.aggression * (1.0 - action.risk) * profile.confidence
            uncertainty_bonus = action.information_gain * self.information_weight * (1.0 - profile.confidence)
            risk_penalty = self.risk_weight * action.risk * (0.5 + profile.aggression * profile.confidence)
            confidence_factor = 0.5 + 0.5 * max(profile.confidence, eval_conf)
            score = action.base_score + matchup + opponent_pressure + uncertainty_bonus - risk_penalty
            score *= confidence_factor
            scored.append((score, action))

        best_score, best = max(scored, key=lambda item: (item[0], item[1].base_score, item[1].action_id))
        rationale = (
            f"selected={best.action_id}; opponent_aggression={profile.aggression:.3f}; "
            f"opponent_confidence={profile.confidence:.3f}; evaluation_confidence={eval_conf:.3f}; "
            f"risk={best.risk:.3f}; information_gain={best.information_gain:.3f}"
        )
        return MultiAgentPlanResult(
            best.action_id, best_score, opponent_id,
            profile.aggression * (1.0 - profile.consistency),
            profile.confidence, rationale
        )
