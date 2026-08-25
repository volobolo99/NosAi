from app.static_data.data_gateway import CachePolicy, DataGateway


class FakeProvider:
    name = "test-api"

    def __init__(self, value=None, error=False):
        self.value = value
        self.error = error

    def fetch(self, dataset):
        if self.error:
            raise ConnectionError("provider unavailable")
        return self.value


def test_gateway_prefers_online_provider():
    gateway = DataGateway(
        FakeProvider({"id": 1}),
        {"items": CachePolicy(ttl_seconds=60)},
    )
    assert gateway.get("items") == {"id": 1}
    assert gateway.is_fresh("items")


def test_gateway_uses_validated_cache_when_provider_fails():
    provider = FakeProvider({"id": 1})
    gateway = DataGateway(
        provider,
        {"items": CachePolicy(ttl_seconds=60, allow_stale_fallback=True)},
    )
    assert gateway.get("items") == {"id": 1}

    provider.error = True
    assert gateway.get("items") == {"id": 1}


def test_gateway_rejects_empty_remote_value():
    gateway = DataGateway(FakeProvider(None), {"items": CachePolicy(ttl_seconds=60)})
    try:
        gateway.get("items")
    except ValueError as exc:
        assert "items" in str(exc)
    else:
        raise AssertionError("empty provider value must be rejected")
