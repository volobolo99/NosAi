from app.client import ClientState
from app.diagnostics import run_preflight


class HealthyClient:
    def check_connection(self):
        return True

    def read_state(self):
        return ClientState(tick=1, payload={"player": {"hp": 100}})

    def validate_action(self, action):
        return action is None

    def close(self):
        return None


class BrokenClient:
    def check_connection(self):
        raise RuntimeError("client transport unavailable")

    def read_state(self):
        raise AssertionError("must not read state after connection failure")

    def validate_action(self, action):
        return False

    def close(self):
        return None


def test_preflight_without_client_is_ready():
    report = run_preflight(modules=("app",), require_client=False, require_torch=False)
    assert report.status == "READY"
    assert any(c.status == "SKIP" for c in report.checks)


def test_preflight_connected_client_is_ready():
    report = run_preflight(
        client_adapter=HealthyClient(),
        modules=("app",),
        require_client=True,
        require_torch=False,
    )
    assert report.status == "READY"
    client = next(c for c in report.checks if c.check_id == "NOSAI-CLIENT-0001")
    assert client.status == "PASS"
    assert "STATE_READ=tick=1" in client.actual
    assert "ACTION_VALIDATE=DRY_RUN_OK" in client.actual


def test_preflight_client_failure_is_blocking_and_diagnostic():
    report = run_preflight(
        client_adapter=BrokenClient(),
        modules=("app",),
        require_client=True,
        require_torch=False,
    )
    assert report.status == "BLOCKED"
    client = next(c for c in report.checks if c.check_id == "NOSAI-CLIENT-0001")
    assert client.status == "FAIL"
    assert client.severity == "BLOCKER"
    assert client.error_type == "RuntimeError"
    assert "client transport unavailable" in client.exception
