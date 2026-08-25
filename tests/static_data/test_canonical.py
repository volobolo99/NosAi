import pytest

from app.static_data.canonical import DatasetNormalizer, DatasetValidationError, validate_references


def test_normalizer_accepts_mapping_payload():
    dataset = DatasetNormalizer().normalize(
        "items",
        {"100": {"name": "Sword"}, "200": {"name": "Shield"}},
        source="api",
    )
    assert dataset.ids() == {"100", "200"}
    assert dataset.records[0].source == "api"


def test_normalizer_accepts_list_with_id():
    dataset = DatasetNormalizer().normalize("skills", [{"id": 7, "name": "Hit"}])
    assert dataset.records[0].record_id == "7"


def test_normalizer_rejects_missing_id():
    with pytest.raises(DatasetValidationError, match="no id"):
        DatasetNormalizer().normalize("skills", [{"name": "Hit"}])


def test_reference_validator_reports_unknown_ids():
    dataset = DatasetNormalizer().normalize(
        "monsters", [{"id": 1, "drop_item_id": 999}]
    )
    missing = validate_references(dataset, {"drop_item_id": {"100", "200"}})
    assert missing == ["monsters:1:drop_item_id=999"]
