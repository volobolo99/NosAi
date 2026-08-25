from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
import random
from typing import Any, Iterable

from app.m3.counterfactual_memory import CounterfactualMemory
from app.m3.graph import CausalGraph


@dataclass(frozen=True)
class CausalCandidate:
    """Intervention-backed causal candidate with uncertainty diagnostics."""

    source: str
    target: str
    effect: float
    confidence: float
    samples: int
    weighted_samples: float
    sign_consistency: float
    standard_error: float
    status: str
    ci_lower: float = 0.0
    ci_upper: float = 0.0
    effect_stability: float = 0.0
    context_support: float = 0.0
    heterogeneity: float = 0.0


class CausalDiscovery:
    """Discover conservative, intervention-backed causal candidates.

    M6.1 provides the basic intervention aggregation. M6.2 adds uncertainty
    quantification, context coverage and heterogeneity checks so a candidate
    is promoted only when its estimated effect is both stable and supported.
    """

    def __init__(
        self,
        *,
        min_samples: int = 2,
        min_confidence: float = 0.60,
        min_effect: float = 0.0,
        bootstrap_samples: int = 400,
        bootstrap_seed: int = 17,
        require_ci_exclusion: bool = True,
        max_heterogeneity: float = 0.75,
    ):
        if min_samples < 1:
            raise ValueError("min_samples must be >= 1")
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError("min_confidence must be in [0, 1]")
        if min_effect < 0.0:
            raise ValueError("min_effect must be >= 0")
        if bootstrap_samples < 20:
            raise ValueError("bootstrap_samples must be >= 20")
        if not 0.0 <= max_heterogeneity <= 1.0:
            raise ValueError("max_heterogeneity must be in [0, 1]")
        self.min_samples = int(min_samples)
        self.min_confidence = float(min_confidence)
        self.min_effect = float(min_effect)
        self.bootstrap_samples = int(bootstrap_samples)
        self.bootstrap_seed = int(bootstrap_seed)
        self.require_ci_exclusion = bool(require_ci_exclusion)
        self.max_heterogeneity = float(max_heterogeneity)

    def discover(
        self,
        memory: CounterfactualMemory,
        *,
        target: str = "value",
        intervention_keys: Iterable[str] | None = None,
    ) -> list[CausalCandidate]:
        keys = set(intervention_keys or ())
        groups: dict[str, list[tuple[float, float, tuple[str, ...]]]] = {}

        for record in memory.records:
            if not record.intervention:
                continue
            context_signature = tuple(sorted(str(k) for k in record.context.keys()))
            for key in record.intervention:
                if keys and key not in keys:
                    continue
                weight = max(0.0, min(1.0, float(record.confidence)))
                if weight == 0.0:
                    continue
                groups.setdefault(str(key), []).append(
                    (float(record.delta), weight, context_signature)
                )

        candidates: list[CausalCandidate] = []
        for source, rows in sorted(groups.items()):
            candidate = self._estimate(source, target, rows)
            if candidate is not None:
                candidates.append(candidate)
        return candidates

    def promote(
        self,
        graph: CausalGraph,
        candidates: Iterable[CausalCandidate],
        *,
        overwrite: bool = False,
    ) -> list[CausalCandidate]:
        promoted: list[CausalCandidate] = []
        for candidate in candidates:
            if candidate.status != "supported":
                continue
            if abs(candidate.effect) < self.min_effect:
                continue
            graph.add_node(candidate.source)
            graph.add_node(candidate.target)
            if any(e.source == candidate.source and e.target == candidate.target for e in graph.edges):
                if not overwrite:
                    continue
                graph.edges = [
                    e for e in graph.edges
                    if not (e.source == candidate.source and e.target == candidate.target)
                ]
            try:
                graph.add_edge(candidate.source, candidate.target, candidate.effect)
            except ValueError:
                continue
            promoted.append(candidate)
        return promoted

    def _estimate(
        self,
        source: str,
        target: str,
        rows: list[tuple[float, float, tuple[str, ...]]],
    ) -> CausalCandidate | None:
        if len(rows) < self.min_samples:
            return None
        total_weight = sum(weight for _, weight, _ in rows)
        if total_weight <= 0:
            return None

        mean = sum(delta * weight for delta, weight, _ in rows) / total_weight
        variance = sum(weight * (delta - mean) ** 2 for delta, weight, _ in rows) / total_weight
        standard_error = sqrt(variance / max(1.0, total_weight))

        non_zero = [delta for delta, _, _ in rows if abs(delta) > 1e-12]
        if not non_zero:
            sign_consistency = 1.0
        else:
            dominant_sign = 1 if mean >= 0 else -1
            sign_consistency = sum(
                1 for delta in non_zero if (1 if delta > 0 else -1) == dominant_sign
            ) / len(non_zero)

        ci_lower, ci_upper = self._bootstrap_interval(rows)
        effect_stability = self._effect_stability(rows)
        context_support = len({ctx for _, _, ctx in rows}) / max(1, len(rows))
        heterogeneity = self._heterogeneity(rows)

        sample_support = min(1.0, total_weight / max(1.0, self.min_samples * 2.0))
        noise_support = abs(mean) / (abs(mean) + standard_error + 1e-9)
        ci_support = 1.0 if ci_lower > 0.0 or ci_upper < 0.0 else 0.0
        confidence = max(
            0.0,
            min(
                1.0,
                0.25 * sample_support
                + 0.25 * sign_consistency
                + 0.15 * noise_support
                + 0.15 * effect_stability
                + 0.10 * context_support
                + 0.10 * ci_support,
            ),
        )
        supported = confidence >= self.min_confidence
        if self.require_ci_exclusion and ci_lower <= 0.0 <= ci_upper:
            supported = False
        if heterogeneity > self.max_heterogeneity:
            supported = False
        status = "supported" if supported else "candidate"

        return CausalCandidate(
            source=source,
            target=target,
            effect=mean,
            confidence=confidence,
            samples=len(rows),
            weighted_samples=total_weight,
            sign_consistency=sign_consistency,
            standard_error=standard_error,
            status=status,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            effect_stability=effect_stability,
            context_support=context_support,
            heterogeneity=heterogeneity,
        )

    def _bootstrap_interval(
        self, rows: list[tuple[float, float, tuple[str, ...]]]
    ) -> tuple[float, float]:
        """Deterministic weighted bootstrap percentile interval."""
        rng = random.Random(self.bootstrap_seed + len(rows))
        values = [delta for delta, _, _ in rows]
        weights = [weight for _, weight, _ in rows]
        total = sum(weights)
        if len(values) < 2 or total <= 0:
            mean = values[0] if values else 0.0
            return mean, mean
        estimates: list[float] = []
        for _ in range(self.bootstrap_samples):
            sample = rng.choices(values, weights=weights, k=len(values))
            estimates.append(sum(sample) / len(sample))
        estimates.sort()
        lo = estimates[max(0, int(0.025 * len(estimates)))]
        hi = estimates[min(len(estimates) - 1, int(0.975 * len(estimates)))]
        return float(lo), float(hi)

    @staticmethod
    def _effect_stability(rows: list[tuple[float, float, tuple[str, ...]]]) -> float:
        signs = [1 if d > 0 else -1 if d < 0 else 0 for d, _, _ in rows]
        nonzero = [s for s in signs if s]
        if not nonzero:
            return 0.0
        dominant = 1 if sum(nonzero) >= 0 else -1
        return sum(s == dominant for s in nonzero) / len(nonzero)

    @staticmethod
    def _heterogeneity(rows: list[tuple[float, float, tuple[str, ...]]]) -> float:
        values = [d for d, _, _ in rows]
        if len(values) < 2:
            return 0.0
        mean_abs = sum(abs(v) for v in values) / len(values)
        if mean_abs <= 1e-12:
            return 0.0
        spread = max(values) - min(values)
        return min(1.0, spread / (spread + mean_abs + 1e-9))
