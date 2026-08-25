from app.client import ClientState
from app.client.loader import ClientAdapterLoadError, load_client_adapter
from app.client.probe import run_client_probe


class GoodAdapter:
    def check_connection(self):
        return True

    def read_state(self):
        return ClientState(tick=7, payload={"player": {"hp": 100}})

    def validate_action(self, action):
        assert action is None
        return True

    def close(self):
        return None


class BadStateAdapter(GoodAdapter):
    def read_state(self):
        return {"tick": 7}


def test_client_probe_is_non_destructive():
    assert run_client_probe(GoodAdapter()) == [
        ("CONNECTION", "CONNECTED"),
        ("STATE_READ", "tick=7"),
        ("ACTION_VALIDATE", "DRY_RUN_OK"),
    ]


def test_client_probe_rejects_invalid_state():
    try:
        run_client_probe(BadStateAdapter())
    except TypeError as exc:
        assert "ClientState" in str(exc)
    else:
        raise AssertionError("invalid client state must block the probe")


def test_loader_requires_explicit_configuration():
    try:
        load_client_adapter(None)
    except ClientAdapterLoadError as exc:
        assert "NOSAI-CLIENT-0002" in str(exc)
    else:
        raise AssertionError("missing adapter configuration must fail")
