import pytest

from nosai.ai.inference import ReadOnlyInference


def test_inference_is_deterministic_and_bounded():
    model = ReadOnlyInference()
    features = {"hp": 100.0, "mp": 40.0, "x": 10.0, "y": 20.0, "level": 30.0}
    first = model.predict("s-19", features)
    second = model.predict("s-19", features)
    assert first == second
    assert 0.0 <= first.score <= 1.0
    assert 0.0 <= first.confidence <= 1.0


def test_invalid_features_are_rejected():
    model = ReadOnlyInference()
    with pytest.raises(ValueError):
        model.predict("s-19", {})
    with pytest.raises(ValueError):
        model.predict("s-19", {"hp": float("inf")})
