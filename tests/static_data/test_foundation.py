import pytest

from app.static_data.data_gateway import CachePolicy, DataGateway
from app.static_data.manifest import StaticManifest
from app.static_data.providers import ProviderError


class Provider:
    name = "test"
    version = "2026.08"

    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def fetch(self, dataset):
        if self.error:
            raise self.error
        return self.value


def test_gateway_does_not_cache_invalid_provider_value():
    gateway = DataGateway(Provider(value=None), {"items": CachePolicy(60)})
    with pytest.raises(ValueError):
        gateway.get("items")
    assert not gateway.is_fresh("items")


def test_gateway_uses_stale_cache_only_after_provider_failure():
    provider = Provider(value={"id": 1})
    gateway = DataGateway(provider, {"items": CachePolicy(60, True)})
    assert gateway.get("items") == {"id": 1}

    provider.error = ProviderError("offline")
    assert gateway.get("items") == {"id": 1}


def test_gateway_does_not_hide_provider_failure_when_stale_fallback_disabled():
    provider = Provider(value={"id": 1})
    gateway = DataGateway(provider, {"items": CachePolicy(60, False)})
    gateway.get("items")
    provider.error = ProviderError("offline")
    with pytest.raises(ProviderError):
        gateway.get("items")


def test_gateway_persists_cache_and_provenance(tmp_path):
    cache_path = tmp_path / "cache.bin"
    provider = Provider(value={"id": 7})
    first = DataGateway(provider, {"items": CachePolicy(60)}, cache_path)
    assert first.get("items") == {"id": 7}
    assert first._cache["items"].version == "2026.08"

    provider.error = ProviderError("offline")
    second = DataGateway(provider, {"items": CachePolicy(60, True)}, cache_path)
    assert second.get("items") == {"id": 7}


def test_manifest_rejects_malformed_dataset_entry():
    with pytest.raises(ValueError, match="must be an object"):
        StaticManifest.from_mapping({
            "schema_version": 1,
            "project": "NosAi",
            "datasets": {"items": "invalid"},
        })


def test_manifest_accepts_valid_dataset_entries():
    manifest = StaticManifest.from_mapping({
        "schema_version": 1,
        "project": "NosAi",
        "datasets": {"items": {"required": True, "version": "1"}},
    })
    assert manifest.datasets[0].name == "items"
    assert manifest.datasets[0].required is True
