import pytest

from app.static_data.providers import HTTPDataProvider, ProviderError


def test_http_provider_delegates_dataset_and_timeout():
    calls = []

    def fetch(dataset, timeout):
        calls.append((dataset, timeout))
        return {"dataset": dataset}

    provider = HTTPDataProvider(fetch)
    assert provider.fetch("items") == {"dataset": "items"}
    assert calls == [("items", 10.0)]


def test_http_provider_wraps_transport_errors():
    def fetch(dataset, timeout):
        raise TimeoutError("timeout")

    provider = HTTPDataProvider(fetch)
    with pytest.raises(ProviderError, match="items"):
        provider.fetch("items")
