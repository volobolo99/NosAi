"""Economic simulation based on the supplied NosAi architecture specification."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Ingredient:
    name: str
    quantity_per_attempt: int
    unit_price: int

    def __post_init__(self) -> None:
        if self.quantity_per_attempt < 0 or self.unit_price < 0:
            raise ValueError("ingredient quantity and price cannot be negative")


@dataclass(frozen=True)
class UpgradeEvaluation:
    item_name: str
    verdict: str
    gold_bazar_price: int
    gold_expected_make: float
    gold_worst_case_90: int
    eur_buy_direct: float
    eur_make_expected: float
    eur_make_worst: float
    eur_savings: float
    success_rate: float


class ExtendedMakeOrBuyOptimizer:
    """Compare expected and 90%-confidence make cost with NosBazar price.

    RMT is represented only as a valuation conversion factor. The optimizer
    does not recommend or facilitate external RMT transactions.
    """

    @staticmethod
    def attempts_for_confidence(success_rate: float, confidence: float = 0.90) -> int:
        if not 0.0 < success_rate <= 1.0:
            raise ValueError("success_rate must be in (0, 1]")
        if not 0.0 < confidence < 1.0:
            raise ValueError("confidence must be in (0, 1)")
        if success_rate == 1.0:
            return 1
        return math.ceil(math.log1p(-confidence) / math.log1p(-success_rate))

    def evaluate_with_rmt(
        self,
        item_name: str,
        success_rate: float,
        gold_per_attempt: int,
        protection_scroll_price: int,
        ingredients: Sequence[Ingredient],
        base_item_price: int,
        bazar_target_price: int,
        rmt_rate_eur_per_million: float,
    ) -> UpgradeEvaluation:
        if min(gold_per_attempt, protection_scroll_price, base_item_price, bazar_target_price) < 0:
            raise ValueError("prices cannot be negative")
        if rmt_rate_eur_per_million < 0:
            raise ValueError("EUR conversion rate cannot be negative")
        if not item_name.strip():
            raise ValueError("item_name must not be empty")

        mat_cost = sum(i.quantity_per_attempt * i.unit_price for i in ingredients)
        cost_per_try = gold_per_attempt + protection_scroll_price + mat_cost
        expected_attempts = 1.0 / success_rate if 0.0 < success_rate <= 1.0 else 0.0
        attempts_90 = self.attempts_for_confidence(success_rate)
        expected_make = base_item_price + expected_attempts * cost_per_try
        worst_make = base_item_price + attempts_90 * cost_per_try
        eur_buy = bazar_target_price / 1_000_000 * rmt_rate_eur_per_million
        eur_make_exp = expected_make / 1_000_000 * rmt_rate_eur_per_million
        eur_make_worst = worst_make / 1_000_000 * rmt_rate_eur_per_million
        verdict = "BUY_NOSBAZAR" if expected_make >= bazar_target_price else "MAKE_SAFE"
        return UpgradeEvaluation(
            item_name=item_name,
            verdict=verdict,
            gold_bazar_price=bazar_target_price,
            gold_expected_make=expected_make,
            gold_worst_case_90=round(worst_make),
            eur_buy_direct=round(eur_buy, 2),
            eur_make_expected=round(eur_make_exp, 2),
            eur_make_worst=round(eur_make_worst, 2),
            eur_savings=round(abs(eur_make_exp - eur_buy), 2),
            success_rate=success_rate,
        )
