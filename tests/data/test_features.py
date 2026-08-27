import pytest

from nosai.data.features import ObservationFeatureExtractor, SCHEMA_VERSION


def test_feature_extraction_is_deterministic_and_versioned():
    extractor = ObservationFeatureExtractor()
    result = extractor.extract("s-17", "2026-08-27T15:00:00+00:00", {"hp": 100, "mp": 40, "x": 12, "y": 7, "level": 10})
    assert result.schema_version == SCHEMA_VERSION
    assert result.values == {"hp": 100.0, "mp": 40.0, "x": 12.0, "y": 7.0, "level": 10.0}
    assert result.quality == 1.0


def test_invalid_and_non_finite_values_are_excluded():
    extractor = ObservationFeatureExtractor()
    result = extractor.extract("s-17", "2026-08-27T15:00:00+00:00", {"hp": "bad", "mp": float("inf"), "x": 3})
    assert result.values == {"x": 3.0}
    assert result.quality == 0.2


def test_input_contract_is_rejected():
    extractor = ObservationFeatureExtractor()
    with pytest.raises(ValueError):
        extractor.extract("", "2026-08-27T15:00:00+00:00", {"hp": 1})
    with pytest.raises(ValueError):
        extractor.extract("s", "not-a-time", {"hp": 1})
