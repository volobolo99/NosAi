import pytest

from nosai.ai.evaluation import InferenceEvaluator


def test_evaluation_computes_bounded_metrics():
    result = InferenceEvaluator().evaluate([
        {"score": 0.2, "confidence": 0.8, "feedback": "ok"},
        {"score": 0.6, "confidence": 0.4},
    ])
    assert result.samples == 2
    assert result.mean_score == pytest.approx(0.4)
    assert result.mean_confidence == pytest.approx(0.6)
    assert result.feedback_rate == pytest.approx(0.5)


def test_evaluation_handles_malformed_items_without_crashing():
    result = InferenceEvaluator().evaluate([{"score": "bad"}, None])
    assert result.samples == 2
    assert result.mean_score == 0.0
    assert result.mean_confidence == 0.0


def test_evaluation_rejects_empty_input():
    with pytest.raises(ValueError):
        InferenceEvaluator().evaluate([])
