from __future__ import annotations

import pytest

from app.nostale_perception.metrics import classification_accuracy, numeric_metric


def test_numeric_metric_reports_mae_rmse_and_tolerance_rate() -> None:
    result = numeric_metric([100, 90, 50], [100, 80, 55], tolerance=5)
    assert result.count == 3
    assert result.mae == pytest.approx(5.0)
    assert result.rmse == pytest.approx((25 / 3) ** 0.5)
    assert result.within_tolerance == pytest.approx(2 / 3)


def test_numeric_metric_rejects_length_mismatch() -> None:
    with pytest.raises(ValueError):
        numeric_metric([1], [1, 2], 1)


def test_classification_accuracy_handles_none_as_a_real_expected_state() -> None:
    assert classification_accuracy(["player", None, "mob"], ["player", None, "npc"]) == pytest.approx(2 / 3)


def test_empty_metric_is_explicitly_unavailable() -> None:
    result = numeric_metric([], [], 1)
    assert result.count == 0
    assert result.mae is None
    assert result.rmse is None
    assert result.within_tolerance is None
