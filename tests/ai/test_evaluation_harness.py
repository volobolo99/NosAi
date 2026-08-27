import pytest

from nosai.ai.evaluation_harness import EvaluationHarness


def test_harness_is_deterministic_and_aggregates_feedback():
    samples = [
        {"score": 0.2, "confidence": 0.8, "feedback": "ok"},
        {"score": 0.6, "confidence": 0.4},
    ]
    harness = EvaluationHarness()
    first = harness.run(samples)
    second = harness.run(samples)
    assert first == second
    assert first.samples == 2
    assert first.valid == 2
    assert first.invalid == 0
    assert first.mean_score == pytest.approx(0.4)
    assert first.mean_confidence == pytest.approx(0.6)
    assert first.feedback_rate == pytest.approx(0.5)


def test_harness_isolates_invalid_samples():
    report = EvaluationHarness().run([
        {"score": 0.5, "confidence": 0.5},
        {"score": "bad", "confidence": 0.5},
        None,
    ])
    assert (report.valid, report.invalid) == (1, 2)
    assert report.mean_score == pytest.approx(0.5)


def test_harness_rejects_empty_dataset():
    with pytest.raises(ValueError):
        EvaluationHarness().run([])
