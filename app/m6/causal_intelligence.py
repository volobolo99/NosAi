from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence
import math

from app.m1.core.types import Action, State
from app.m2.causal import CounterfactualEngine
from app.m2.imagination import ImaginationEngine
from app.m2.types import CounterfactualResult
from app.m3.counterfactual_memory import CounterfactualMemory
from app.m3.graph import CausalGraph
from app.m6.causal_discovery import CausalCandidate, CausalDiscovery


@dataclass(frozen=True)
class InterventionProposal:
    intervention: dict[str, float]
    expected_effect: float
    confidence: float
    source: str
    information_gain: float = 0.0
    risk: float = 0.0
    cost: float = 1.0
    value_of_information: float = 0.0
    score: float = 0.0


@dataclass(frozen=True)
class CausalPlanScore:
    action: Action
    causal_effect: float
    empirical_effect: float
    uncertainty: float
    confidence: float
    score: float
    counterfactual_score: float = 0.0
    accepted: bool = False
    rationale: tuple[str, ...] = ()


@dataclass(frozen=True)
class CausalPlanResult:
    """Auditable causal action-selection result.

    The selected action is produced only after combining causal evidence,
    empirical intervention memory and an explicit World-Model counterfactual
    comparison.
    """

    action: Action
    candidates: tuple[CausalPlanScore, ...]
    baseline_action: Action
    used_counterfactual: bool
    confidence: float
    rationale: tuple[str, ...] = ()


@dataclass(frozen=True)
class CounterfactualOutcome:
    """One measurable outcome of a counterfactual comparison."""

    name: str
    baseline: float
    intervention: float
    delta: float
    uncertainty: float
    confidence: float
    risk_delta: float = 0.0


@dataclass(frozen=True)
class CounterfactualComparisonV2:
    """Auditable multi-outcome counterfactual result.

    `utility_delta` is a weighted aggregate, while `outcomes` preserves each
    individual outcome so callers never lose the underlying evidence.
    """

    baseline: Any
    intervention: Any
    outcomes: tuple[CounterfactualOutcome, ...]
    utility_delta: float
    risk_delta: float
    uncertainty: float
    confidence: float
    causal_evidence: float
    decision_score: float
    accepted: bool


class InterventionPlanner:
    """Select experiments by expected utility *and* expected information gain."""
    def __init__(
        self,
        discovery: CausalDiscovery | None = None,
        *,
        information_weight: float = 0.35,
        effect_weight: float = 0.45,
        confidence_weight: float = 0.20,
        risk_weight: float = 0.30,
        default_cost: float = 1.0,
    ):
        if min(information_weight, effect_weight, confidence_weight, risk_weight) < 0:
            raise ValueError("planner weights must be non-negative")
        if default_cost <= 0:
            raise ValueError("default_cost must be > 0")
        self.discovery = discovery or CausalDiscovery()
        self.information_weight = float(information_weight)
        self.effect_weight = float(effect_weight)
        self.confidence_weight = float(confidence_weight)
        self.risk_weight = float(risk_weight)
        self.default_cost = float(default_cost)

    def propose(
        self,
        candidates: Iterable[CausalCandidate],
        *,
        values: Iterable[float] = (-1.0, 1.0),
        max_proposals: int | None = None,
        risk_budget: float = 1.0,
    ) -> list[InterventionProposal]:
        if risk_budget < 0:
            raise ValueError("risk_budget must be >= 0")
        proposals: list[InterventionProposal] = []
        seen: set[tuple[str, float]] = set()
        for c in candidates:
            if c.status not in {"supported", "candidate"}:
                continue
            uncertainty = min(1.0, abs(c.standard_error) / (abs(c.effect) + abs(c.standard_error) + 1e-9))
            uncertainty = min(1.0, 0.5 * uncertainty + 0.5 * (1.0 - c.context_support))
            information_gain = min(1.0, uncertainty * (1.0 + 0.25 * max(0, 1 - c.samples)))
            risk = min(1.0, max(0.0, 0.5 * c.heterogeneity + 0.5 * (1.0 - c.confidence)))
            for raw_value in values:
                value = float(raw_value)
                key = (c.source, value)
                if key in seen:
                    continue
                seen.add(key)
                expected = float(c.effect * value)
                effect_value = max(0.0, expected)
                confidence_value = max(0.0, min(1.0, c.confidence))
                cost = self.default_cost
                voi = (self.information_weight * information_gain + self.effect_weight * effect_value + self.confidence_weight * confidence_value - self.risk_weight * risk) / cost
                proposals.append(InterventionProposal({c.source: value}, expected, confidence_value, "discovery", information_gain, risk, cost, voi, voi))
        ranked = sorted(proposals, key=lambda p: (p.score, p.information_gain, p.expected_effect, p.confidence), reverse=True)
        selected: list[InterventionProposal] = []
        spent = 0.0
        for proposal in ranked:
            if spent + proposal.risk > risk_budget + 1e-12:
                continue
            selected.append(proposal)
            spent += proposal.risk
            if max_proposals is not None and len(selected) >= max_proposals:
                break
        return selected


class CounterfactualEngineV2:
    """Evidence-aware counterfactual evaluator.

    V2 keeps the original World-Model rollout as the source of predictions,
    but exposes an auditable multi-outcome comparison.  It combines model
    uncertainty, risk change, empirical memory evidence and causal-graph
    evidence.  The legacy ``compare`` API remains available and returns the
    original ``CounterfactualResult`` for backwards compatibility.
    """

    def __init__(
        self,
        imagination: ImaginationEngine,
        *,
        memory: CounterfactualMemory | None = None,
        causal_graph: CausalGraph | None = None,
        utility_weights: Mapping[str, float] | None = None,
        risk_weight: float = 0.5,
        uncertainty_weight: float = 0.5,
        causal_weight: float = 0.35,
        empirical_weight: float = 0.25,
        min_confidence: float = 0.50,
        max_risk_delta: float = 1.0,
    ):
        if min_confidence < 0 or min_confidence > 1:
            raise ValueError("min_confidence must be in [0, 1]")
        if max_risk_delta < 0:
            raise ValueError("max_risk_delta must be >= 0")
        for value in (risk_weight, uncertainty_weight, causal_weight, empirical_weight):
            if value < 0:
                raise ValueError("weights must be non-negative")
        self.engine = CounterfactualEngine(imagination)
        self.memory = memory
        self.causal_graph = causal_graph
        self.utility_weights = dict(utility_weights or {})
        self.risk_weight = float(risk_weight)
        self.uncertainty_weight = float(uncertainty_weight)
        self.causal_weight = float(causal_weight)
        self.empirical_weight = float(empirical_weight)
        self.min_confidence = float(min_confidence)
        self.max_risk_delta = float(max_risk_delta)

    def compare(self, state: State, baseline: list[Action], intervention: list[Action]) -> CounterfactualResult:
        result = self.engine.compare(state, baseline, intervention)
        confidence = self._confidence(result.intervention.uncertainty, result.delta_risk, result.confidence)
        return CounterfactualResult(result.baseline, result.intervention, result.delta_return, result.delta_risk, confidence)

    def compare_detailed(
        self,
        state: State,
        baseline: Sequence[Action],
        intervention: Sequence[Action],
        *,
        intervention_key: str | None = None,
        intervention_value: float | None = None,
        outcome_weights: Mapping[str, float] | None = None,
        causal_evidence: float | None = None,
    ) -> CounterfactualComparisonV2:
        result = self.engine.compare(state, list(baseline), list(intervention))
        weights = dict(self.utility_weights)
        weights.update(outcome_weights or {})

        base_unc = max(0.0, float(result.baseline.uncertainty))
        int_unc = max(0.0, float(result.intervention.uncertainty))
        aggregate_unc = min(1.0, 0.5 * (base_unc + int_unc))
        outcomes = [
            CounterfactualOutcome(
                "return",
                float(result.baseline.discounted_return),
                float(result.intervention.discounted_return),
                float(result.delta_return),
                aggregate_unc,
                self._confidence(aggregate_unc, result.delta_risk, result.confidence),
                float(result.delta_risk),
            ),
            CounterfactualOutcome(
                "risk",
                float(result.baseline.terminal_probability),
                float(result.intervention.terminal_probability),
                float(result.delta_risk),
                aggregate_unc,
                self._confidence(aggregate_unc, result.delta_risk, result.confidence),
                float(result.delta_risk),
            ),
            CounterfactualOutcome(
                "uncertainty",
                base_unc,
                int_unc,
                int_unc - base_unc,
                aggregate_unc,
                self._confidence(aggregate_unc, result.delta_risk, result.confidence),
                0.0,
            ),
        ]

        # Optional scalar outcomes can be supplied by callers when their World
        # Model exposes them through trajectory metadata.  Return/risk/uncertainty
        # remain the canonical outcomes and are always present.
        if intervention_key is not None and intervention_value is not None:
            evidence = self._evidence_for(intervention_key, intervention_value)
        else:
            evidence = 0.0
        if causal_evidence is not None:
            evidence = max(0.0, min(1.0, float(causal_evidence)))

        utility_delta = self._weighted_utility(outcomes, weights)
        uncertainty_penalty = self.uncertainty_weight * aggregate_unc
        risk_penalty = self.risk_weight * max(0.0, result.delta_risk)
        decision_score = (
            utility_delta
            + self.causal_weight * evidence
            - uncertainty_penalty
            - risk_penalty
        )
        confidence = self._confidence(aggregate_unc, result.delta_risk, result.confidence)
        accepted = confidence >= self.min_confidence and result.delta_risk <= self.max_risk_delta
        return CounterfactualComparisonV2(
            result.baseline,
            result.intervention,
            tuple(outcomes),
            utility_delta,
            float(result.delta_risk),
            aggregate_unc,
            confidence,
            evidence,
            decision_score,
            accepted,
        )

    def compare_from_intervention(
        self,
        state: State,
        baseline: Sequence[Action],
        intervention: Sequence[Action],
        proposal: InterventionProposal,
        *,
        outcome_weights: Mapping[str, float] | None = None,
    ) -> CounterfactualComparisonV2:
        key, value = next(iter(proposal.intervention.items()))
        return self.compare_detailed(
            state,
            baseline,
            intervention,
            intervention_key=key,
            intervention_value=value,
            outcome_weights=outcome_weights,
            causal_evidence=proposal.confidence,
        )

    def _evidence_for(self, key: str, value: float) -> float:
        scores: list[float] = []
        if self.memory is not None:
            rows = self.memory.query({key: value}, limit=self.memory.max_records)
            if rows:
                scores.append(sum(max(0.0, min(1.0, r.confidence)) for r in rows) / len(rows))
        if self.causal_graph is not None:
            edges = [e for e in self.causal_graph.children(key)]
            if edges:
                scores.append(min(1.0, sum(abs(e.weight) for e in edges) / len(edges)))
        if not scores:
            return 0.0
        return sum(scores) / len(scores)

    @staticmethod
    def _weighted_utility(outcomes: Sequence[CounterfactualOutcome], weights: Mapping[str, float]) -> float:
        default = {"return": 1.0, "risk": -1.0, "uncertainty": -0.5}
        total = 0.0
        normalizer = 0.0
        for outcome in outcomes:
            weight = float(weights.get(outcome.name, default.get(outcome.name, 0.0)))
            total += weight * outcome.delta
            normalizer += abs(weight)
        return total / normalizer if normalizer else 0.0

    @staticmethod
    def _confidence(uncertainty: float, risk_delta: float, base_confidence: float) -> float:
        value = float(base_confidence)
        value *= 1.0 / (1.0 + max(0.0, uncertainty))
        value *= max(0.0, 1.0 - max(0.0, risk_delta))
        return max(0.0, min(1.0, value))


class CausalPlanner:
    """Select actions using discovery, intervention proposals and counterfactuals.

    ``rank`` remains a cheap evidence-only path. ``plan`` is the full M6.5
    path: discover intervention-backed causes, generate value-of-information
    proposals, evaluate each actionable candidate against a baseline in the
    learned World Model, then select only an accepted counterfactual winner.
    """
    def __init__(
        self,
        graph: CausalGraph,
        memory: CounterfactualMemory,
        *,
        causal_weight: float = 0.55,
        empirical_weight: float = 0.20,
        counterfactual_weight: float = 0.25,
        counterfactual_engine: CounterfactualEngineV2 | None = None,
        discovery: CausalDiscovery | None = None,
        intervention_planner: InterventionPlanner | None = None,
    ):
        if min(causal_weight, empirical_weight, counterfactual_weight) < 0:
            raise ValueError("planner weights must be non-negative")
        total = causal_weight + empirical_weight + counterfactual_weight
        if total <= 0:
            raise ValueError("at least one planner weight must be positive")
        self.graph = graph
        self.memory = memory
        self.causal_weight = float(causal_weight) / total
        self.empirical_weight = float(empirical_weight) / total
        self.counterfactual_weight = float(counterfactual_weight) / total
        self.discovery = discovery or CausalDiscovery()
        self.intervention_planner = intervention_planner or InterventionPlanner(self.discovery)
        self.counterfactual_engine = counterfactual_engine

    def rank(
        self,
        actions: Iterable[Action],
        *,
        causal_key: str = "action",
        outcome: str = "reward",
    ) -> list[CausalPlanScore]:
        edges = {e.target: e for e in self.graph.children(causal_key)}
        ranked: list[CausalPlanScore] = []
        for action in actions:
            value = self._action_value(action, causal_key)
            edge = edges.get(outcome) or edges.get(causal_key)
            causal = (edge.weight * value) if edge is not None else 0.0
            empirical = self.memory.mean_effect({causal_key: value}) or 0.0
            matching = [r for r in self.memory.records if r.intervention.get(causal_key) == value]
            confidence = (sum(r.confidence for r in matching) / len(matching)) if matching else 0.0
            score = self.causal_weight * causal + self.empirical_weight * empirical
            ranked.append(CausalPlanScore(action, causal, empirical, 0.0, confidence, score))
        return sorted(ranked, key=lambda x: x.score, reverse=True)

    def plan(
        self,
        state: State,
        actions: Iterable[Action],
        *,
        causal_key: str = "action",
        outcome: str = "reward",
        baseline_action: Action | None = None,
        risk_budget: float = 1.0,
        max_proposals: int | None = None,
        outcome_weights: Mapping[str, float] | None = None,
    ) -> CausalPlanResult:
        """Run the complete causal planning loop for the supplied actions."""
        action_list = list(actions)
        if not action_list:
            raise ValueError("actions must not be empty")
        if self.counterfactual_engine is None:
            raise ValueError("counterfactual_engine is required for full causal planning")

        baseline = baseline_action or action_list[0]
        discovered = self.discovery.discover(self.memory, target=outcome, intervention_keys=[causal_key])
        proposals = self.intervention_planner.propose(
            discovered,
            values=self._candidate_values(action_list, causal_key),
            max_proposals=max_proposals,
            risk_budget=risk_budget,
        )
        proposal_by_value = {
            float(next(iter(p.intervention.values()))): p
            for p in proposals
            if p.intervention
        }

        scores: list[CausalPlanScore] = []
        for action in action_list:
            value = self._action_value(action, causal_key)
            proposal = proposal_by_value.get(value)
            if proposal is None:
                scores.append(CausalPlanScore(
                    action, 0.0, self.memory.mean_effect({causal_key: value}) or 0.0,
                    1.0, 0.0, float("-inf"), 0.0, False, ("no_supported_intervention_proposal",),
                ))
                continue
            comparison = self.counterfactual_engine.compare_from_intervention(
                state, [baseline], [action], proposal, outcome_weights=outcome_weights
            )
            empirical = self.memory.mean_effect({causal_key: value}) or 0.0
            causal_effect = proposal.expected_effect
            final_score = (
                self.causal_weight * causal_effect
                + self.empirical_weight * empirical
                + self.counterfactual_weight * comparison.decision_score
            )
            rationale = (
                "causal_evidence",
                "intervention_proposal",
                "world_model_counterfactual",
            )
            if not comparison.accepted:
                final_score -= 1.0 + abs(comparison.risk_delta)
                rationale += ("counterfactual_rejected",)
            scores.append(CausalPlanScore(
                action, causal_effect, empirical, comparison.uncertainty,
                comparison.confidence, final_score, comparison.decision_score,
                comparison.accepted, rationale,
            ))

        accepted = [row for row in scores if row.accepted]
        pool = accepted or [row for row in scores if row.score != float("-inf")]
        if not pool:
            raise ValueError("no actionable causal candidate")
        winner = max(pool, key=lambda row: (row.score, row.confidence))
        return CausalPlanResult(
            winner.action,
            tuple(sorted(scores, key=lambda row: row.score, reverse=True)),
            baseline,
            True,
            winner.confidence,
            winner.rationale + (("accepted_counterfactual",) if winner.accepted else ("fallback_evidence_rank",)),
        )

    @staticmethod
    def _action_value(action: Action, key: str) -> float:
        raw = action.parameters.get(key, action.parameters.get("value", action.parameters.get("d", 0.0)))
        return float(raw)

    @classmethod
    def _candidate_values(cls, actions: Sequence[Action], key: str) -> tuple[float, ...]:
        return tuple(dict.fromkeys(cls._action_value(action, key) for action in actions))
