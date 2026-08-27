import pytest

from nosai.ai.training import split_dataset, train_baseline


def test_split_is_deterministic_and_disjoint():
    samples = [{"id": i, "score": i / 10} for i in range(10)]
    first = split_dataset(samples)
    second = split_dataset(list(reversed(samples)))
    assert first == second
    assert len(first.train) + len(first.validation) + len(first.test) == 10
    assert not set(map(str, first.train)) & set(map(str, first.validation))
    assert not set(map(str, first.train)) & set(map(str, first.test))


def test_baseline_report_is_reproducible():
    samples = [{"id": i, "score": 0.5} for i in range(10)]
    first = train_baseline(samples)
    second = train_baseline(samples)
    assert first == second
    assert first.baseline_score == pytest.approx(0.5)
    assert len(first.dataset_digest) == 64


def test_empty_dataset_is_rejected():
    with pytest.raises(ValueError):
        train_baseline([])


def test_invalid_split_ratios_are_rejected():
    samples = [{"score": 0.5}]
    with pytest.raises(ValueError):
        split_dataset(samples, train_ratio=0.9, validation_ratio=0.2)
