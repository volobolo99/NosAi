import pytest

from app.static_data.manifest import StaticManifest


def test_manifest_accepts_project_schema():
    manifest = StaticManifest.from_mapping(
        {
            "schema_version": 1,
            "project": "NosAi",
            "snapshot_policy": "immutable-runtime",
            "datasets": {
                "items": {"required": True, "source": "https://example.invalid/items.json"}
            },
        }
    )
    assert manifest.datasets[0].name == "items"
    assert manifest.datasets[0].required is True


def test_manifest_rejects_unknown_schema():
    with pytest.raises(ValueError, match="unsupported"):
        StaticManifest.from_mapping(
            {"schema_version": 99, "project": "NosAi", "datasets": {"items": {}}}
        )
